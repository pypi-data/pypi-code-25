import os
import warnings

import django
import django.apps
from django.conf import settings
from django.core import serializers
from django.core.management import call_command, CommandError
from django.core.management.base import BaseCommand
from django.core.management.commands.loaddata import humanize
from django.db import router, DatabaseError, IntegrityError
from django.utils.encoding import force_text
from django.utils.module_loading import import_string

from ...models import DataModel

DJANGO_LOADDATA_COMMAND = 'django.core.management.commands.loaddata.Command'

LOADDATA_COMMAND_CLASS = getattr(settings, 'DATAMODELS_LOADDATA_COMMAND', DJANGO_LOADDATA_COMMAND)
LoaddataCommand = import_string(LOADDATA_COMMAND_CLASS)


class Command(LoaddataCommand):
    def load_label(self, fixture_label):
        """
        Loads fixtures files for a given label.
        """
        show_progress = self.verbosity >= 3
        for fixture_file, fixture_dir, fixture_name in self.find_fixtures(fixture_label):
            _, ser_fmt, cmp_fmt = self.parse_name(os.path.basename(fixture_file))
            open_method, mode = self.compression_formats[cmp_fmt]
            fixture = open_method(fixture_file, mode)
            try:
                self.fixture_count += 1
                objects_in_fixture = 0
                loaded_objects_in_fixture = 0
                if self.verbosity >= 2:
                    self.stdout.write(
                        "Installing %s fixture '%s' from %s."
                        % (ser_fmt, fixture_name, humanize(fixture_dir))
                    )
                objects = serializers.deserialize(
                    ser_fmt, fixture, using=self.using, ignorenonexistent=self.ignore,
                )

                for obj in objects:
                    objects_in_fixture += 1
                    if router.allow_migrate_model(self.using, obj.object.__class__):
                        self.models.add(obj.object.__class__)
                        try:
                            if obj.object.__class__.objects.filter(id=obj.object.id).exists():
                                continue
                            loaded_objects_in_fixture += 1
                            obj.save(using=self.using)
                            if show_progress:
                                self.stdout.write(
                                    '\rProcessed %i object(s).' % loaded_objects_in_fixture,
                                    ending=''
                                )
                        except (DatabaseError, IntegrityError) as e:
                            e.args = ("Could not load %(app_label)s.%(object_name)s(pk=%(pk)s): %(error_msg)s" % {
                                'app_label': obj.object._meta.app_label,
                                'object_name': obj.object._meta.object_name,
                                'pk': obj.object.pk,
                                'error_msg': force_text(e)
                            },)
                            raise
                if objects and show_progress:
                    self.stdout.write('')  # add a newline after progress indicator
                self.loaded_object_count += loaded_objects_in_fixture
                self.fixture_object_count += objects_in_fixture
            except Exception as e:
                if not isinstance(e, CommandError):
                    e.args = ("Problem installing fixture '%s': %s" % (fixture_file, e),)
                raise
            finally:
                fixture.close()

            # Warn if the fixture we loaded contains 0 objects.
            if objects_in_fixture == 0:
                warnings.warn(
                    "No fixture data found for '%s'. (File format may be "
                    "invalid.)" % fixture_name,
                    RuntimeWarning
                )
