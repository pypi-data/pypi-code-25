import django.apps
from django.contrib.admin.utils import NestedObjects
from django.contrib.sites.models import Site
from django.core import urlresolvers
from django.core.management.base import BaseCommand
from django.urls.exceptions import NoReverseMatch

from datamodels.models import DataModel
from datamodels.services.stale_objects import StaleObjects


class Command(BaseCommand):
    help = 'Loads data for all DataModels'
    verbosity = 1

    def add_arguments(self, parser):
        parser.add_argument(
            'args', metavar='labels', nargs='*',
            help='Module paths to datamodel; can be appname or appname.ModelName'
        )

    def handle(self, *args, **options):
        data_models = self.get_data_models()
        data_models = self.filter_data_models(data_models, args)

        stale_objects = StaleObjects.get_stale_objects(data_models)
        without_related, with_related = StaleObjects.split_objects_by_having_related(stale_objects)
        print('Found %d stale objects...' % (len(with_related) + len(without_related)))

        if without_related:
            print('Stale objects without related (could be removed):')
            for obj in without_related:
                print('  ' + self.get_stale_obj_repr(obj))

        if with_related:
            print('Stale objects with related items - cannot be removed:')
            for obj in with_related:
                print('  ' + self.get_stale_obj_repr(obj))
                collector = NestedObjects(using='default')
                collector.collect([obj])
                self.print_related(collector.nested()[1:], indent=4)

    def print_related(self, related_list, indent=0):
        for related in related_list:
            if isinstance(related, (list, tuple)):
                self.print_related(related, indent+2)
            else:
                print(' ' * indent + self.get_stale_obj_repr(related))

    def get_stale_obj_repr(self, obj):
        try:
            path = urlresolvers.reverse("admin:%s_change" % (obj._meta.label.replace('.', '_').lower()), args=(obj.id,))
            url = 'http://' + Site.objects.all()[0].domain + path
        except NoReverseMatch:
            url = ''

        return "{0}:{1} {2} {3}".format(
            obj._meta.label,
            str(obj.id).ljust(4, ' '),
            unicode(obj).ljust(32, ' '),
            url
        )

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