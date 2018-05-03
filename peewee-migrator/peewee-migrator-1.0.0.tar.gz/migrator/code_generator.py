__all__ = ['CodeGenerator']


class CodeGenerator(object):
    MIGRATION_TEMPLATE = '''{imports}
from playhouse.migrate import migrate


MIGRATION_NAME = {migration_name}
MIGRATION_TIME = {migration_time}
MIGRATION_DEPENDENCIES = {migration_dependencies}


proxy_db = peewee.Proxy()


class BaseModel(peewee.Model):
    class Meta:
        database = proxy_db


{models}{proxies_init}


def up(config):
    proxy_db.initialize(config.get_db())
    migrator = config.get_migrator()
{up}


def down(config):
    proxy_db.initialize(config.get_db())
    migrator = config.get_migrator()
{down}
'''

    def __init__(self, models):
        self.models = models

    class Builder(object):
        def __init__(self, indent=0, indent_step=4):
            self.indent = indent
            self.indent_step = indent_step
            self.lines = []

        def tab(self):
            self.indent += self.indent_step
            return self

        def un_tab(self):
            self.indent -= self.indent_step
            return self

        def write_line(self, text):
            self.lines.append('{}{}'.format(' ' * self.indent, text))
            return self

        @property
        def code(self):
            return '\n'.join(self.lines)

    @classmethod
    def _join_lines_with_indent(cls, lines, indent=4):
        return '\n'.join(['{}{}'.format(' ' * indent, x) for x in lines])

    @classmethod
    def _get_import_by_path(cls, path):
        return '.'.join(path.split('.')[:-1])

    @classmethod
    def prepare_field_code(cls, field, field_name=None):
        if field_name is None:
            field_name = field['name']
        elif field['path'] == 'peewee.DeferredForeignKey':
            field['path'] = 'peewee.ForeignKeyField'
            field['params']['__args'] = field['params']['__args'].replace('"', '').replace("'", '')
            field['params']['field'] = f'{field["params"]["__args"]}.id'

        params = []
        if '__args' in field['params']:
            params.append(field['params'].pop('__args'))
        for k, v in field['params'].items():
            params.append(f'{k}={v}')
        return '{} = {}({})'.format(field_name, field['path'], ', '.join(params))

    def prepare_code(self):
        builder = self.Builder()
        to_import = {'peewee'}
        models_str = []
        prepared = self.prepare_dict()
        for model in prepared['models']:
            builder.write_line('class {}(BaseModel):'.format(model['name']))
            for field in model['fields']:
                for p in model.get('imports', []):
                    to_import.add(p)
                builder.tab().write_line(self.prepare_field_code(field.copy())).un_tab()
            builder.write_line('').tab().write_line('class Meta:')
            builder.tab().write_line('table_name = {}'.format(model['table'].__repr__())).un_tab().un_tab()
            builder.write_line('').write_line('')
        models_str.append(builder.code)
        imports_str = ['import {}'.format(x) for x in to_import]
        return imports_str, models_str, prepared['proxies']

    def prepare_dict(self):
        models_dict = []
        proxies = {}
        for model, db_table, fields in self.models:
            model_data = {'name': model, 'constraints': []}
            fields_json = []
            imports = set()
            for f in fields:
                field = f.copy()
                initial_kwargs = field['params'].get('initial_kwargs', {}).copy()
                import_path = self._get_import_by_path(field['path'])
                params = {}
                if field['params']['index'] and not field['params']['unique']:
                    params['index'] = 'True'
                if field['params']['unique']:
                    params['unique'] = 'True'
                if field['params']['null']:
                    params['null'] = 'True'
                if field['params'].get('default'):
                    field_default = field['params']['default']
                    need_import = field_default.get('import') is not None
                    params['default'] = field_default['value'] if need_import else field_default['value'].__repr__()
                    if need_import:
                        imports.add(field_default['import'])
                db_field = initial_kwargs.pop('db_field', field['column'])
                if db_field and db_field != field['name']:
                    params['column_name'] = db_field.__repr__()
                to_field = initial_kwargs.pop('to_field', {})
                if to_field and to_field['column'] != 'id':
                    params['field'] = to_field['column'].__repr__()
                if initial_kwargs:
                    rel = initial_kwargs.pop('rel_model', None)
                    if rel:
                        if rel == model:
                            rel = 'self'
                        else:
                            proxies.setdefault(rel, set()).add(f'{model}.{field["name"]}')
                            model_data['constraints'].append(field['name'])
                            field['path'] = 'peewee.DeferredForeignKey'
                        params['__args'] = rel.__repr__()

                    for k, v in initial_kwargs.items():
                        if not isinstance(v, dict):
                            params[k] = v.__repr__()
                            continue
                        need_import = v.get('import') is not None
                        params[k] = v['value'] if need_import else v['value'].__repr__()
                        if need_import:
                            imports.add(v['import'])

                field_json = {'path': field['path'], 'params': params, 'name': field['name']}
                if field['fk_name'] is not None:
                    field_json['fk_name'] = field['fk_name']
                if import_path != 'peewee':
                    field_json['import'] = import_path
                    imports.add(import_path)
                fields_json.append(field_json)
            model_data.update({'table': db_table, 'fields': fields_json})
            if imports:
                model_data['imports'] = list(imports)
            models_dict.append(model_data)
        return {
            'proxies': {k: list(v) for k, v in proxies.items()},
            'models': sorted(models_dict, key=lambda x: x['name'])
        }

    @classmethod
    def changes_code(cls, migration, indent=0, revert=False):
        builder = cls.Builder(indent=indent)
        new_constraints = []

        if migration['create']:
            builder.write_line('').write_line('# Tables creation')
            for model, constraints in migration['create']:
                builder.write_line(f'{model}.create_table()')
                new_constraints.extend((model, c) for c in constraints)
        if new_constraints:
            builder.write_line('').write_line('# New constraints creation')
            builder.write_line("if config.db_type != 'sqlite':").tab()
            for model, c in new_constraints:
                builder.write_line(f'{model}._schema.create_foreign_key({model}.{c})')
            builder.un_tab()

        if migration['drop']:
            builder.write_line('').write_line('# Tables deletion')
            for db_table in migration['drop']:
                builder.write_line(f'{db_table}.drop_table()')

        # Tables renaming
        pass

        if migration['fields']['create']:
            builder.write_line('').write_line('# Fields creation')
            if revert:
                # this fields not in migration code
                for i, (table, db_field, field) in enumerate(migration['fields']['create'], 1):
                    new_field = f'DeletedField{i}'
                    builder.write_line(cls.prepare_field_code(field["field"], field_name=new_field))
                    field['field_string'] = new_field
            builder.write_line('migrate(').tab()
            for table, db_field, field in migration['fields']['create']:
                builder.write_line(
                    'migrator.add_column({}, {}, {}),'.format(table.__repr__(), db_field, field['field_string'])
                )

            builder.un_tab().write_line(')')

        if migration['fields']['drop']:
            builder.write_line('').write_line('# Drop fields')
            builder.write_line('migrate(').tab()
            for table, db_field in migration['fields']['drop']:
                builder.write_line('migrator.drop_column({}, {}),'.format(table.__repr__(), db_field))
            builder.un_tab().write_line(')')

        # Fields renaming
        pass

        to_drop = [x for x in migration['fields']['index'] if x[0] == 'drop']
        if to_drop:
            builder.write_line('').write_line('# Drop indexes')
            builder.write_line('migrate(').tab()
            for action, table, db_field in to_drop:
                builder.write_line('migrator.drop_index({}, {}),'.format(table.__repr__(), db_field.__repr__()))
            builder.un_tab().write_line(')')

        to_create = [x for x in migration['fields']['index'] if x[0] == 'add']
        unique = [x for x in to_create if x[-1]]
        index = [x for x in to_create if not x[-1]]
        if index:
            builder.write_line('').write_line('# Create indexes')
            builder.write_line('migrate(').tab()
            for action, table, db_field, is_uniq in index:
                builder.write_line(
                    'migrator.add_index({}, ({},), False),'.format(table.__repr__(), db_field.__repr__())
                )
            builder.un_tab().write_line(')')
        if unique:
            builder.write_line('').write_line('# Create unique indexes')
            builder.write_line('migrate(').tab()
            for action, table, db_field, is_uniq in index:
                builder.write_line(
                    'migrator.add_index({}, ({},), True)),'.format(table.__repr__(), db_field.__repr__())
                )
            builder.un_tab().write_line(')')

        result_code = [builder.code]
        return result_code

    @classmethod
    def migration_code(
        cls, imports, models, up=None, down=None, migration_name=None, proxies=None, dependencies=None,
        migration_time=None, migration_hash=None
    ):
        if migration_name is None:
            migration_name = 'Migration {}'.format(migration_hash)
        if dependencies is None:
            migration_dependencies = []
        else:
            migration_dependencies = '[{}]'.format(', '.join([x['hash'].__repr__() for x in dependencies]))
        if up is None:
            up = ['pass']
        if down is None:
            down = ['pass']
        up = cls._join_lines_with_indent(up)
        down = cls._join_lines_with_indent(down)

        proxy_fields_init = []
        for proxy, fields in proxies.items():
            proxy_fields_init.append(f'peewee.DeferredForeignKey.resolve({proxy})')
            # for f in fields:
            #     proxy_fields_init.append(f'{f}.set_model({proxy})')
        proxy_fields_init = '\n{}'.format('\n'.join(proxy_fields_init)) if proxy_fields_init else ''

        return cls.MIGRATION_TEMPLATE.format(
            up=up, down=down, imports='\n'.join(imports), models='\n\n\n'.join(models),
            migration_name=migration_name.__repr__(), migration_dependencies=migration_dependencies,
            migration_time=migration_time, proxies_init=proxy_fields_init
        )
