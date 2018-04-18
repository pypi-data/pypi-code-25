from django.core.management.base import BaseCommand
import os
from packrat.models import HoardFile


class Command(BaseCommand):
    help = 'Updates file data.'

    def add_arguments(self, parser):
        parser.add_argument('path')

    def handle(self, *args, **options):
        for (dirpath, dirnames, filenames) in os.walk(options['path']):
            self.stdout.write(dirpath)
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                self.stdout.write(filepath)
                hf = HoardFile.objects.filter(path=filepath).first()
                if hf is None:
                    hf = HoardFile(path=filepath)
                hf.update()
                hf.save()
