import inspect

from inspect import getmodule, ismethod, isclass

import peewee
from peewee import ModelBase, ForeignKeyField
from playhouse.reflection import Introspector, UnknownField

from importlib import reload

__all__ = ['Inspector', 'DEFAULT_MIGRATOR_PARAMS']


DEFAULT_MIGRATOR_PARAMS = {
    peewee.CharField: (
        ('max_length', 255),
    )
}


class CustomReflection(Introspector):
    def generate_models(self, skip_invalid=False, table_names=None,
                        literal_column_names=False, bare_fields=False):
        database = self.introspect(table_names=table_names,
                                   literal_column_names=literal_column_names)
        models = {}

        class BaseModel(peewee.Model):
            class Meta:
                database = self.metadata.database
                schema = self.schema

        reflected = set()  # migrator changes

        def _create_model(table, models):
            for foreign_key in database.foreign_keys[table]:
                dest = foreign_key.dest_table

                # migrator changes
                if dest not in models and dest != table and dest not in reflected:
                    # Stop infinite recursion
                    reflected.add(dest)
                    # / migrator changes
                    _create_model(dest, models)

            primary_keys = []
            columns = database.columns[table]
            for column_name, column in columns.items():
                if column.primary_key:
                    primary_keys.append(column.name)

            multi_column_indexes = database.multi_column_indexes(table)
            column_indexes = database.column_indexes(table)

            class Meta:
                indexes = multi_column_indexes
                table_name = table

            # Fix models with multi-column primary keys.
            composite_key = False
            if len(primary_keys) == 0:
                primary_keys = columns.keys()
            if len(primary_keys) > 1:
                Meta.primary_key = peewee.CompositeKey(*[
                    field.name for col, field in columns.items()
                    if col in primary_keys])
                composite_key = True

            attrs = {'Meta': Meta}
            for column_name, column in columns.items():
                FieldClass = column.field_class
                if FieldClass is not ForeignKeyField and bare_fields:
                    FieldClass = peewee.BareField
                elif FieldClass is UnknownField:
                    FieldClass = peewee.BareField

                params = {
                    'column_name': column_name,
                    'null': column.nullable}
                if column.primary_key and composite_key:
                    if FieldClass is peewee.AutoField:
                        FieldClass = peewee.IntegerField
                    params['primary_key'] = False
                elif column.primary_key and FieldClass is not peewee.AutoField:
                    params['primary_key'] = True
                if column.is_foreign_key():
                    if column.is_self_referential_fk():
                        params['model'] = 'self'
                    else:
                        dest_table = column.foreign_key.dest_table
                        # migrator changes
                        if dest_table not in models:
                            params['rel_model_name'] = database.model_names[dest_table]
                            FieldClass = peewee.DeferredForeignKey
                        else:
                            params['model'] = models[dest_table]
                        # / migrator changes
                    if column.to_field:
                        params['field'] = column.to_field

                    # Generate a unique related name.
                    params['backref'] = '%s_%s_rel' % (table, column_name)

                if column.default is not None:
                    constraint = peewee.SQL('DEFAULT %s' % column.default)
                    params['constraints'] = [constraint]

                if column_name in column_indexes and not \
                   column.is_primary_key():
                    if column_indexes[column_name]:
                        params['unique'] = True
                    elif not column.is_foreign_key():
                        params['index'] = True

                attrs[column.name] = FieldClass(**params)

            try:
                models[table] = type(str(database.model_names[table]), (BaseModel,), attrs)  # migrator changes
            except ValueError:
                if not skip_invalid:
                    raise

        # Actually generate Model classes.
        for table, model in sorted(database.model_names.items()):
            if table not in models:
                _create_model(table, models)

        return models


class Inspector(object):
    DEFAULT_PARAMS = (
        ('sequence', None),
        ('default', None),
        ('constraints', None),
        ('schema', None),
        ('on_delete', None),
        ('on_update', None),
        ('extra', None),
        ('primary_key', False)
    )
    models_path = ('app.models',)

    def __init__(self, models_path=None, excluded_models=None):
        if models_path is not None:
            self.models_path = models_path
        self.excluded_models = [] if excluded_models is None else excluded_models
        self._collected_models = set()

    @staticmethod
    def is_model(obj):
        return isclass(obj) and (issubclass(obj, ModelBase) or isinstance(obj, ModelBase))

    def get_models(self):
        for path in self.models_path:
            module = __import__(path, fromlist=['*'])
            models = reload(module)
            for model in dir(models):
                if model[0].isupper() and model[0] != '_':
                    obj = getattr(models, model)
                    if self.is_model(obj) and model not in self.excluded_models:
                        yield model, obj

    def get_database_models(self, db=None):
        i = CustomReflection.from_database(db)
        return i.generate_models().values()

    def inspect_models(self):
        for model, model_obj in self.get_models():
            if model in self._collected_models:
                # prevent doubles for imported models
                continue
            self._collected_models.add(model)
            yield self.inspect_model(model_obj, model=model)
        self._collected_models = set()

    def inspect_database(self, db):
        models = self.get_database_models(db)
        for model_obj in models:
            if model_obj.__name__ in self.excluded_models:
                continue
            yield self.inspect_model(model_obj)

    def inspect_model(self, model_obj, model=None):
        if model is None:
            model = model_obj.__name__
        fields = list(self.collect_fields(model_obj._meta.sorted_fields, model=model))
        return model, model_obj._meta.table_name, fields

    @classmethod
    def get_param_value(cls, value):
        primitive_types = (int, str, bytes, bool)
        if isinstance(value, primitive_types):
            # Raw type
            return {'value': value}

        if not callable(value):
            # Mutable type, do not apply automatically
            return None
        _module = inspect.getmodule(value)
        if _module is not None:
            # Simple functions
            module_name = _module.__name__
            return {'value': '{}.{}'.format(module_name, value.__name__), 'import': module_name}
        # datetime case
        if value.__name__ == 'now' and type(value).__name__ == 'builtin_function_or_method':
            return {'value': 'datetime.datetime.now', 'import': 'datetime'}
        # TODO: Process builtins with _module = None
        return None

    @classmethod
    def get_field_initial_params(cls, field):
        param_keys = [*cls.DEFAULT_PARAMS]
        param_keys.extend(getattr(field, 'MIGRATOR_PARAMS', ()))
        if type(field) in DEFAULT_MIGRATOR_PARAMS:
            param_keys.extend(DEFAULT_MIGRATOR_PARAMS[type(field)])
        return tuple(set(param_keys))

    def collect_fields(self, sorted_fields, model=''):
        for field in sorted_fields:
            is_fk = isinstance(field, ForeignKeyField)
            name = field.name
            if name == 'id' and isinstance(field, peewee.AutoField):
                # Skip auto-generated id
                continue
            field_path = field.__class__.__name__
            field_module = getmodule(field.__class__)
            if field_module is not None:
                field_module = field_module.__name__
                field_path = '{}.{}'.format(field_module, field_path)

            default_value = self.get_param_value(field.default)
            field_params = {
                'index': field.index, 'unique': field.unique, 'null': field.null,
                'initial_kwargs': {}
            }
            if default_value is not None:
                field_params['default'] = default_value

            for param in self.get_field_initial_params(field):
                if not isinstance(param, str):
                    param, default_val = param
                    param_obj = getattr(field, param, None)
                    if (default_val is None and param_obj is None) or (default_val is False and param_obj is False):
                        continue
                    if param_obj == default_val:
                        continue
                else:
                    param_obj = getattr(field, param, None)
                if ismethod(param_obj):
                    continue

                field_params['initial_kwargs'][param] = self.get_param_value(param_obj)

            if field.name != field.column_name:
                if not is_fk or (is_fk and field.column_name != f'{field.name}_id'):
                    field_params['initial_kwargs']['column_name'] = field.column_name

            db_column = field.column_name

            if isinstance(field, ForeignKeyField):
                # Save only model name
                field_params['initial_kwargs']['rel_model'] = field.rel_field.model.__name__
                # Field normalization
                db_column = field.name if field.column_name == f'{field.name}_id' else field.column_name
                to_field = {
                    'name': field.rel_field.name, 'column': field.rel_field.column_name
                }
                if to_field['name'] == 'id' and to_field['column'] == 'id':
                    field_params['initial_kwargs'].pop('to_field', None)
                else:
                    field_params['initial_kwargs']['to_field'] = to_field

            if not field_params['initial_kwargs']:
                field_params.pop('initial_kwargs', None)

            yield {
                'name': name, 'column': db_column, 'path': field_path, 'params': field_params,
                'fk_name': field.column_name if is_fk else None
            }
