import django
from django.contrib.admin.utils import NestedObjects

from datamodels.models import DataModel
from datamodels.services.fixtures_parser import FixtureParser


class StaleObjects(object):
    @classmethod
    def get_stale_objects(cls, datamodels=None):
        stale_objects = []
        datamodels = datamodels or [model for model in django.apps.apps.get_models() if issubclass(model, DataModel)]
        for model in datamodels:
            if not getattr(model.DataModelMeta, 'fixtures', []):
                continue
            stale_objects += cls.get_stale_objects_for_model(model)
        return stale_objects

    @classmethod
    def split_objects_by_having_related(cls, objects):
        with_related = []
        without_related = []
        for obj in objects:
            collector = NestedObjects(using='default')
            collector.collect([obj])
            if len(collector.nested()) > 1:  # first record is the object itself
                with_related.append(obj)
            else:
                without_related.append(obj)
        return without_related, with_related

    @classmethod
    def get_stale_objects_for_model(cls, model):
        data = cls.get_model_fixtures_data(model)
        pks = cls.get_ids_from_fixtures_data(data)
        return list(model.objects.exclude(pk__in=pks))

    @classmethod
    def get_ids_from_fixtures_data(cls, objects):
        return list([obj['pk'] for obj in objects])

    @classmethod
    def get_model_fixtures_data(cls, model):
        data = []
        for fixture_label in getattr(model.DataModelMeta, 'fixtures', []):
            fixture_file = FixtureParser.find_fixtures(fixture_label)[0][0]
            data += FixtureParser.parse_fixture(fixture_file)
        return data

