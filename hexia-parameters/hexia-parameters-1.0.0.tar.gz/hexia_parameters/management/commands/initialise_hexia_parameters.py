from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils.text import slugify

from hexia_parameters.models import Parameter

parameters = settings.HEXIA_PARAMETERS_LIST

class Command(BaseCommand):
    help = 'Sets Up initial hexia_parameter data'

    def handle(self, *args, **options):
        for p in settings.HEXIA_PARAMETERS_LIST:
            p, created = Parameter.objects.get_or_create (name = p)
            p.save()