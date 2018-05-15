import django
import django.apps
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string

from ...models import DataModel

DJANGO_LOADDATA_COMMAND = 'django.core.management.commands.loaddata.Command'
LOADDATA_COMMAND_CLASS = getattr(settings, 'DATAMODELS_LOADDATA_COMMAND_CLASS', DJANGO_LOADDATA_COMMAND)
LoaddataCommand = import_string(LOADDATA_COMMAND_CLASS)


class Command(BaseCommand):
    help = 'Loads data for all DataModels'
    verbosity = 1

    def add_arguments(self, parser):
        parser.add_argument(
            'args', metavar='labels', nargs='*',
            help='Module paths to datamodel; can be appname or appname.ModelName'
        )

    def handle(self, *args, **options):
        self.verbosity = options['verbosity']

        data_models = self.get_data_models()
        data_models = self.filter_data_models(data_models, args)

        loaded_models = []
        for model in data_models:
            self.load_model_fixtures(model, loaded_models=loaded_models)

    def get_data_models(self):
        return [model for model in django.apps.apps.get_models() if issubclass(model, DataModel)]

    @staticmethod
    def filter_data_models(data_models, filter_labels):
        if not filter_labels:
            return data_models
        filtered_data_models = []
        for filter in filter_labels:
            for model in data_models:
                if model._meta.label.lower() == filter.lower():  # Assume label
                    filtered_data_models.append(model)
                elif model._meta.app_label.lower() == filter.lower():  # Assume app label
                    filtered_data_models.append(model)
        return filtered_data_models

    def load_model_fixtures(self, model, loaded_models):
        if model in loaded_models:
            return

        self.load_dependencies(model, loaded_models)

        fixtures = getattr(model.DataModelMeta, 'fixtures', None) or []
        for fixture in fixtures:
            if self.verbosity >= 1:
                print("Loading %s..." % fixture)
            if django.VERSION < (1, 10):
                # Django 1.8 and 1.9 doesn't support command class as call_command's first argument
                # So we need to extract command name from path
                # 1. django.core.management.commands.loaddata.Command => loaddata.Command
                # 2. loaddata.Command => ['loaddata', 'Command'][0]
                command_name = LOADDATA_COMMAND_CLASS.split('commands.')[-1].split('.')[0]
                call_command(command_name, fixture, verbosity=self.verbosity, skip_checks=True)
            else:
                call_command(LoaddataCommand(), fixture, verbosity=self.verbosity, skip_checks=True)

            if self.verbosity >= 1:
                print('')

        default_fixtures = getattr(model.DataModelMeta, 'default_fixtures', None) or []
        for fixture in default_fixtures:
            if self.verbosity >= 1:
                print("Loading default %s..." % fixture)
            call_command('datamodels_loaddata_default', fixture, verbosity=self.verbosity, skip_checks=True)
            if self.verbosity >= 1:
                print('')

        loaded_models.append(model)

    def load_dependencies(self, model, loaded_models):
        if not issubclass(model, DataModel):
            raise Exception('%s was set as datamodel dependency, but it\'s not a DataModel' % (unicode(model)))

        dependencies = getattr(model.DataModelMeta, 'dependencies', None) or []
        for dep_model_str in dependencies:
            app_label, model_name = dep_model_str.split('.')
            dep_model = django.apps.apps.get_model(model_name=model_name, app_label=app_label)
            self.load_model_fixtures(dep_model, loaded_models=loaded_models)
