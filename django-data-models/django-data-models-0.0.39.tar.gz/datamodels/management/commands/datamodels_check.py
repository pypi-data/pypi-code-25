import django.apps
from django.core.management.base import BaseCommand

from ...models import DataModel
from ...services.fixtures_parser import FixtureParser


class Command(BaseCommand):
    help = 'Checks data for all DataModels'
    verbosity = 1

    def add_arguments(self, parser):
        parser.add_argument(
            'args', metavar='labels', nargs='*',
            help='Module paths to datamodel; can be appname or appname.ModelName'
        )

    def handle(self, *args, **options):
        print('Checking datamodels...')
        self.check_datamodels_meta_exists()
        self.check_meta_has_fixtures()
        self.check_datamodels_inheritance()
        self.check_fixtures_for_correct_content_type()

    def check_meta_has_fixtures(self):
        for model in self.get_data_models():
            meta = getattr(model, 'DataModelMeta', None)
            fixtures = getattr(meta, 'fixtures', [])
            default_fixtures = getattr(meta, 'default_fixtures', [])
            if not fixtures and not default_fixtures:
                print("  %s.DataModelMeta doesn't use fixtures or default_fixtures " % model._meta.label)

    def check_datamodels_meta_exists(self):
        for model in self.get_data_models():
            meta = getattr(model, 'DataModelMeta', None)
            if meta is None:
                print("  %s doesn't have DataModelMeta" % model._meta.label)
                continue

    def check_datamodels_inheritance(self):
        for model in django.apps.apps.get_models():
            if hasattr(model, 'DataModelMeta') and not issubclass(model, DataModel):
                print("  %s has DataModelMeta but it's not a child of DataModel" % model._meta.label)

    def check_fixtures_for_correct_content_type(self):
        for model in self.get_data_models():
            meta = getattr(model, 'DataModelMeta', None)
            fixtures = getattr(meta, 'fixtures', [])
            default_fixtures = getattr(meta, 'default_fixtures', [])

            for fixture_label in fixtures + default_fixtures:
                for fixture_file, fixture_dir, fixture_name in FixtureParser.find_fixtures(fixture_label):
                    objects = FixtureParser.parse_fixture(fixture_file)
                    for obj in objects:
                        if obj['model'] != model._meta.label.lower():
                            print('%s have a datafixture %s which have an object with different content type %s' % (
                                model._meta.label, fixture_label, obj['model']
                            ))

    def get_data_models(self):
        return [model for model in django.apps.apps.get_models() if issubclass(model, DataModel)]
