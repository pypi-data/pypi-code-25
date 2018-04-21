from django.core.management.base import BaseCommand
import os
from packrat.models import HoardFile


class Command(BaseCommand):
    help = 'Updates file data.'

    def add_arguments(self, parser):
        parser.add_argument('path')

    def handle(self, *args, **options):
        path = options['path']
        if os.path.isfile(path):
            self._process_file(path)
            return

        for (dirpath, dirnames, filenames) in os.walk(options['path']):
            self.stdout.write(dirpath)
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                self._process_file(filepath)

    def _process_file(self, filepath):
        self.stdout.write(filepath)
        hf = HoardFile.objects.filter(path=filepath).first()
        if hf is None:
            hf = HoardFile(path=filepath)
        hf.update()
        hf.save()
