import django.apps
from django.conf import settings
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
        old_app = None
        for model in data_models:
            if model._meta.app_label != old_app:
                print model._meta.app_label
                old_app = model._meta.app_label

            print('    %s' % model.__name__)

            meta = getattr(model, 'DataModelMeta', DataModel.DataModelMeta)
            fixtures = getattr(meta, 'fixtures', [])
            default_fixtures = getattr(meta, 'default_fixtures', [])

            if fixtures:
                print('        fixtures: %s' % ', '.join(fixtures))
            if default_fixtures:
                print('        default fixtures: %s' % ', '.join(default_fixtures))

    def get_data_models(self):
        return [model for model in django.apps.apps.get_models() if issubclass(model, DataModel)]
