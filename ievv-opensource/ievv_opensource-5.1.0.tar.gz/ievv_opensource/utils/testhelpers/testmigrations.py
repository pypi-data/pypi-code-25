from django import test
from django.core.management import call_command
from django.db import connection
from django.db.migrations.loader import MigrationLoader


class MigrationTestCase(test.TransactionTestCase):
    """
    Test case for a Django database migration.

    Example::

        class TestSomeMigrations(MigrationTestCase):
            migrate_from = '0002_previous_migration'
            migrate_to = '0003_migration_being_tested'

            def test_is_selected_is_flipped(self):
                MyModel = self.apps_before.get_model('myapp', 'MyModel')
                MyModel.objects.create(
                    name='Test1',
                    is_selected=True
                )
                MyModel.objects.create(
                    name='Test2',
                    is_selected=False
                )
                MyModel.objects.create(
                    name='Test3',
                    is_selected=True
                )

                self.migrate()

                MyModel = self.apps_after.get_model('myapp', 'MyModel')
                self.assertEqual(MyModel.objects.filter(is_selected=True).count, 1)
                self.assertEqual(MyModel.objects.filter(is_selected=False).count, 2)
    """

    #: The django app_label for the app you are migrating. This is the same app_label as you
    #: use with ``python manage.py makemigrations <app_label>`` to create the migration.
    app_label = None

    #: The name of the migration to migrate from.
    #: Can be the full name, or just the number (I.E.: ``0002`` or ``0002_something``.
    migrate_from = None

    #: The name of the migration to migrate to.
    #: Can be the full name, or just the number (I.E.: ``0003`` or ``0003_something``.
    migrate_to = None

    def setUp(self):
        """
        Perform required setup.

        If you override ``setUp()``, you must call ``super().setUp()``!
        """
        if not self.app_label or not self.migrate_from or not self.migrate_to:
            raise ValueError('app_label, migrate_from and migrate_to must be specified.')
        self._migrate_from_list = [(self.app_label, self.migrate_from)]
        self._migrate_to_list = [(self.app_label, self.migrate_to)]
        self._apps_before = self._get_apps_for_migration(self._migrate_from_list)
        self._apps_after = None
        for app_label, migration_name in self._migrate_from_list:
            self._run_migrate(app_label, migration_name)

    def _get_apps_for_migration(self, migration_states):
        loader = MigrationLoader(connection)
        full_names = []
        for app_label, migration_name in migration_states:
            if migration_name != 'zero':
                migration_name = loader.get_migration_by_prefix(app_label, migration_name).name
                full_names.append((app_label, migration_name))
        state = loader.project_state(full_names)
        return state.apps

    @property
    def apps_before(self):
        """
        Get an ``apps`` object just like the first argument to a Django data migration
        at the state before migration has been run.

        Only available **before** :meth:`.migrate` has been called, or after :meth:`.reverse_migrate`
        has been called.
        """
        if self._apps_after is not None:
            raise AttributeError('apps_before is only available before migrate() has been run, '
                                 'or after reverse_migrate().')
        return self._apps_before

    @property
    def apps_after(self):
        """
        Get an ``apps`` object just like the first argument to a Django data migration
        at the state after migration has been run, and not available after :meth:`.reverse_migrate`
        has been called (unless :meth:`.migrate` is called again).

        Only available **after** :meth:`.migrate` has been called.
        """
        if self._apps_after is None:
            raise AttributeError('apps_after is only available after migrate() has been run. '
                                 'It is not available after reverse_migrate() unless migrate() '
                                 'has been run again.')
        return self._apps_after

    def migrate(self):
        """
        Migrate the database from :obj:`.migrate_from` to :obj:`.migrate_to`.
        """
        if self._apps_after is not None:
            raise Exception('migrate() already run. Can not run migrate() multiple times '
                            'without running reverse_migrate() in between.')

        for app_label, migration_name in self._migrate_to_list:
            self._run_migrate(app_label, migration_name)
        self._apps_after = self._get_apps_for_migration(self._migrate_to_list)

    def reverse_migrate(self):
        """
        Migrate the database from :obj:`.migrate_to` to :obj:`.migrate_from`.

        You must call :meth:`.migrate` before calling this.
        """
        if self._apps_after is None:
            raise Exception('You must run migrate() before you can run reverse_migrate().')

        for app_label, migration_name in self._migrate_from_list:
            self._run_migrate(app_label, migration_name)
        self._apps_after = None

    def get_migrate_command_kwargs(self):
        """
        Get kwargs for the ``migrate`` management command.

        The defaults are sane, by you may want to override this and change
        the ``verbosity`` argument for debugging purposes.
        """
        return {'verbosity': 0,
                'no_initial_data': True,
                'interactive': False}

    def _run_migrate(self, app_label, migration_name, fake=False):
        kwargs = self.get_migrate_command_kwargs()
        kwargs['fake'] = fake
        args = ('migrate', app_label, migration_name)
        call_command(*args, **kwargs)
