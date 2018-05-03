import datetime
import hashlib
import json
import os
import sys
import time

import peewee

from migrator.code_generator import CodeGenerator
from migrator.collector import ChangesCollector
from migrator.db_inspector import Inspector

__all__ = ['Executor']


def extend_path(path, index=0):
    for p in reversed(path.split(':')):
        if p not in sys.path:
            sys.path.insert(index, p)


database_storage = peewee.Proxy()


class DatabaseStorageBackend(peewee.Model):
    revision = peewee.CharField(max_length=32, unique=True)
    applied_at = peewee.DateTimeField(default=datetime.datetime.now)
    faked = peewee.BooleanField(default=False)

    class Meta:
        table_name = 'migrator_migrations'
        database = database_storage


class Executor(object):
    CodeGenerator = CodeGenerator
    STATUS_APPLIED = 'applied'
    STATUS_AVAILABLE = 'available'
    REQUIRED_FILE = 'required.json'

    def __init__(self, config):
        self.config = config
        # Need to correct work
        extend_path(config.get_setting(config.MIGRATOR_SYS_PATH), 1)
        self.migrations_in_path = False
        self._db_storage_initialized = False

    def init_db_storage(self):
        if self._db_storage_initialized:
            return
        database_storage.initialize(self.get_db_obj())
        DatabaseStorageBackend.create_table(safe=True)
        self._db_storage_initialized = True

    def _extend_migrations(self):
        if not self.migrations_in_path:
            extend_path(self.config.get_setting(self.config.MIGRATOR_MIGRATIONS_DIR), 0)
            self.migrations_in_path = True

    def import_migration(self, migration):
        return __import__(migration['import'])

    def get_migrations(self):
        migrations_dir = self.config.get_setting(self.config.MIGRATOR_MIGRATIONS_DIR)
        # Need to make __import__ works
        self._extend_migrations()

        for f in os.listdir(migrations_dir):
            if f.startswith('migration_') and f.endswith('.py'):
                revision = f.split('migration_', 1)[-1].rsplit('.py', 1)[0]
                yield self.fetch_migration(revision)

    def get_migrations_by_hash(self, base_hash, migrations=None):
        migrations = self.get_migrations() if migrations is None else migrations
        return [x for x in migrations if x['hash'].startswith(base_hash)]

    def fetch_migration(self, revision):
        self._extend_migrations()
        migration = __import__('migration_{}'.format(revision))
        return {
            'time': migration.MIGRATION_TIME,
            'name': migration.MIGRATION_NAME,
            'hash': revision,
            'file': 'migration_{}.py'.format(revision),
            'import': 'migration_{}'.format(revision),
            'dependencies': migration.MIGRATION_DEPENDENCIES,
            # is applied
            'status': self.check_status(revision),
            'required': self.check_required_position(revision)
        }

    def apply(self, migration, fake=False):
        if not fake:
            _module = self.import_migration(migration)
            _module.up(config=self.config)
        self.make_applied(migration['hash'], fake=fake)

    def revert(self, migration, fake=False):
        if not fake:
            _module = self.import_migration(migration)
            _module.down(self.config)
        self.unmake_applied(migration['hash'])

    def get_applied_fs(self):
        migrations_dir = self.config.get_setting(self.config.MIGRATOR_MIGRATIONS_DIR)
        try:
            with open(os.path.join(migrations_dir, '.applied.json'), 'r', encoding='utf-8') as f:
                return json.loads(f.read())
        except:
            return []

    def get_applied_db(self):
        self.init_db_storage()
        return [x.revision for x in DatabaseStorageBackend.select(DatabaseStorageBackend.revision)]

    def get_applied(self):
        if self.config.storage_type == self.config.STORAGE_FS:
            return self.get_applied_fs()
        else:
            return self.get_applied_db()

    def get_required(self):
        migrations_dir = self.config.get_setting(self.config.MIGRATOR_MIGRATIONS_DIR)
        try:
            with open(os.path.join(migrations_dir, self.REQUIRED_FILE), 'r', encoding='utf-8') as f:
                return json.loads(f.read())
        except:
            return []

    def make_required(self, revision, after=None):
        required = self.get_required()
        position = len(required)  # Last one
        if after is not None:
            try:
                position = required.index(after) + 1
            except ValueError:
                pass
        required.insert(position, revision)
        self.save_required_fs(required)

    def make_applied(self, revision, fake=False):
        if self.config.storage_type == self.config.STORAGE_FS:
            applied = set(self.get_applied())
            applied.add(revision)
            self.save_applied_fs(applied)
        else:
            self.save_applied_db(revision, fake=fake)

    def unmake_applied(self, revision):
        if self.config.storage_type == self.config.STORAGE_FS:
            applied = set(self.get_applied())
            applied.remove(revision)
            self.save_applied_fs(applied)
        else:
            self.save_applied_db(revision, revert=True)

    def save_applied_fs(self, applied):
        migrations_dir = self.config.get_setting(self.config.MIGRATOR_MIGRATIONS_DIR)
        with open(os.path.join(migrations_dir, '.applied.json'), 'w', encoding='utf-8') as f:
            f.write(json.dumps(list(applied)))

    def save_applied_db(self, revision, revert=False, fake=False):
        self.init_db_storage()
        if revert:
            return DatabaseStorageBackend.delete().where(DatabaseStorageBackend.revision == revision).execute() == 1
        DatabaseStorageBackend.create(revision=revision, faked=fake)
        return True

    def save_required_fs(self, required):
        migrations_dir = self.config.get_setting(self.config.MIGRATOR_MIGRATIONS_DIR)
        with open(os.path.join(migrations_dir, self.REQUIRED_FILE), 'w', encoding='utf-8') as f:
            f.write(json.dumps(required))

    def check_status(self, revision):
        applied = self.get_applied()

        return self.STATUS_APPLIED if revision in applied else self.STATUS_AVAILABLE

    def check_required_position(self, revision):
        required = self.get_required()

        try:
            return required.index(revision)
        except ValueError:
            return None

    def check_dependencies(self, migration):
        return all([self.check_status(dep) == self.STATUS_APPLIED for dep in migration['dependencies']])

    def get_db_obj(self):
        return self.config.get_db()

    def check_migrations_package(self):
        migrations_path = self.config.get_setting(self.config.MIGRATOR_MIGRATIONS_DIR)
        os.makedirs(migrations_path, exist_ok=True)
        init_path = os.path.join(migrations_path, '__init__.py')
        if not os.path.exists(init_path):
            with open(init_path, 'w') as f:
                f.write('')

    def make_empty_migration(self, migration_name=None):
        i = Inspector(models_path=self.config.get_models_paths(), excluded_models=self.config.get_excluded())
        current_models = list(i.inspect_models())
        c = CodeGenerator(current_models)
        imports, models, proxies = c.prepare_code()
        new = {x['name']: x for x in c.prepare_dict()['models']}
        return self.migrate(imports, models, proxies, new, new, migration_name=migration_name)

    def migrate_from_migration(self, migration=None, migration_name=None):
        excluded_models = self.config.get_excluded()
        # Get old state from models
        i = Inspector(models_path=[migration['import']], excluded_models=excluded_models)
        old_models = list(i.inspect_models())
        old = {x['name']: x for x in CodeGenerator(old_models).prepare_dict()['models']}
        # Get current state from models
        i = Inspector(models_path=self.config.get_models_paths(), excluded_models=excluded_models)
        current_models = list(i.inspect_models())
        new = {x['name']: x for x in CodeGenerator(current_models).prepare_dict()['models']}
        # Generate code and new models
        c = CodeGenerator(current_models + old_models)
        imports, models, proxies = c.prepare_code()
        return self.migrate(
            imports, models, proxies, new, old, migration_name=migration_name, dependencies=[migration]
        )

    def migrate_from_db(self, migration_name=None):
        excluded_models = self.config.get_excluded()
        i = Inspector(models_path=self.config.get_models_paths(), excluded_models=excluded_models)
        # Get current state from models
        current_models = list(i.inspect_models())
        new = {x['name']: x for x in CodeGenerator(current_models).prepare_dict()['models']}
        # Get state from database
        db_models = list(i.inspect_database(self.get_db_obj()))
        old = {x['name']: x for x in CodeGenerator(db_models).prepare_dict()['models']}
        # Generate code
        current_models_tables = [m[1] for m in current_models]
        for db_model in db_models:
            if db_model[1] not in current_models_tables:
                current_models.append(db_model)
        c = CodeGenerator(current_models)
        imports, models, proxies = c.prepare_code()
        return self.migrate(imports, models, proxies, new, old, migration_name=migration_name, merge_by_table=True)

    def migrate(self, imports, models, proxies, new, old, migration_name=None, dependencies=None, merge_by_table=False):
        up_migration = self._get_migration_changes(new=new, old=old)
        up = self.CodeGenerator.changes_code(up_migration, indent=4)
        down_new, down_old = old, new
        if merge_by_table:
            by_table_name = {v['table']: v['name'] for v in new.values()}
            old_model_names = {v['table']: v['name'] for v in old.values()}
            old_to_new_names = {v: by_table_name.get(k, v) for k, v in old_model_names.items()}
            down_new = {}
            for k, v in old.items():
                model_name = by_table_name.get(v['table'], v['name'])
                down_fields = []
                for f in v.get('fields', []):
                    if f['path'] != 'peewee.DeferredForeignKey':
                        down_fields.append(f)
                        continue
                    field = f.copy()
                    params = field.get('params', {}).copy()
                    arg = params['__args'][1:-1]
                    if arg in old_to_new_names:
                        arg = old_to_new_names[arg]
                    params['__args'] = f"'{arg}'"
                    field['params'] = params
                    down_fields.append(field)

                down_new[model_name] = {**v, **{'name': model_name, 'fields': down_fields}}

        down_migration = self._get_migration_changes(new=down_new, old=down_old)
        down = self.CodeGenerator.changes_code(down_migration, indent=4, revert=True)
        return self.make_migration(
            imports, models, up=up, down=down, migration_name=migration_name, proxies=proxies,
            dependencies=dependencies
        )

    def _get_migration_changes(self, new, old, revert=False):
        collector = ChangesCollector()
        model_matches = collector.get_table_matches(new, old)
        migration = {
            'drop': [x for x in old.keys() if x not in model_matches.values()],
            'create': [(x, new[x]['constraints']) for x in new.keys() if x not in model_matches.keys()],
            'rename': [],
            'fields': {
                'rename': [],
                'create': [],
                'drop': [],
                'index': [],
                'null': []
            }
        }
        for new_model_name, old_model_name in model_matches.items():
            new_model = new[new_model_name]
            old_model = old[old_model_name]
            # Table renaming case
            if new_model['table'] != old_model['table']:
                migration['rename'].append((old_model['table'], new_model['table']))

            # Fields diff
            new_fields = {x['name']: x for x in new[new_model_name]['fields']}
            old_fields = {x['name']: x for x in old[old_model_name]['fields']}

            field_matches = collector.get_field_matches(new[new_model_name]['fields'], new_fields, old_fields)
            # Fields diff ops
            migration['fields']['drop'].extend(
                collector.get_columns_to_drop(new_fields, old_fields, new_model, old_model, field_matches)
            )
            migration['fields']['create'].extend(
                collector.get_columns_to_create(new_fields, old_fields, new_model, old_model, field_matches)
            )

            for new_field_name, old_field_name in field_matches.items():
                new_field = new_fields[new_field_name]
                old_field = old_fields[old_field_name]
                migration['fields']['index'].extend(
                    collector.get_field_indexes(new_field, old_field, new_model, old_model))
                migration['fields']['null'].extend(collector.get_field_null(new_field, old_field, new_model, old_model))
                # Fields renaming case
                migration['fields']['rename'].extend(
                    collector.get_field_rename(new_field, old_field, new_model, old_model)
                )

        return migration

    def make_migration(
        self, imports, models, up=None, down=None, migration_name=None, proxies=None, dependencies=None
    ):

        self.check_migrations_package()

        migration_time = int(time.time())
        migration_hash = hashlib.md5(str(migration_time).encode('utf-8')).hexdigest()

        migration_kwargs = locals()
        migration_kwargs.pop('self', None)

        migration_path = os.path.join(
            self.config.get_setting(self.config.MIGRATOR_MIGRATIONS_DIR),
            'migration_{}.py'.format(migration_hash)
        )
        migration_code = self.CodeGenerator.migration_code(**migration_kwargs)

        with open(migration_path, 'w', encoding='utf-8') as f:
            f.write(migration_code)

        return migration_hash

    def _get_tables_as_models(self, db=None):
        db = self.get_db_obj() if db is None else db

        class BaseModel(peewee.Model):
            class Meta:
                database = db

        for table in db.get_tables():
            model = type('_', (BaseModel,), {})
            model._meta.table_name = table
            yield model

    def drop_all(self, db=None):
        for model in self._get_tables_as_models(db=db):
            model.drop_table(cascade=True)

    def truncate_all(self, db=None):
        db = self.get_db_obj() if db is None else db
        db_type = self.config.db_type
        if db_type == 'mysql':
            db.execute_sql('SET foreign_key_checks = 0;')
        for table in db.get_tables():
            if db_type in ('mysql', 'sqlite'):
                delim = '"' if db_type == 'sqlite' else '`'
                db.execute_sql(f'TRUNCATE TABLE {delim}{table}{delim}')
            else:
                db.execute_sql(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE')
        if db_type == 'mysql':
            db.execute_sql('SET foreign_key_checks = 1;')
