import gzip
import json
import os
import yaml

from django.core import serializers
from django.core.management.commands.loaddata import Command as LoaddataCommand, SingleZipReader
from django.db import DEFAULT_DB_ALIAS


class FixtureParser(object):
    COMPRESSION_FORMATS = {
        None: (open, 'r'),
        'gz': (gzip.GzipFile, 'rb'),
        'zip': (SingleZipReader, 'r'),
    }

    @classmethod
    def get_loaddata_command_instance(cls):
        loaddata_command = LoaddataCommand()
        loaddata_command.using = DEFAULT_DB_ALIAS
        loaddata_command.serialization_formats = serializers.get_public_serializer_formats()
        loaddata_command.compression_formats = cls.COMPRESSION_FORMATS
        loaddata_command.verbosity = 0
        loaddata_command.app_label = None
        return loaddata_command

    @classmethod
    def find_fixtures(cls, labels):
        loaddata_command = cls.get_loaddata_command_instance()
        return loaddata_command.find_fixtures(labels)

    @classmethod
    def parse_fixture(cls, fixture_file):
        loaddata_command = cls.get_loaddata_command_instance()
        _, ser_fmt, cmp_fmt = loaddata_command.parse_name(os.path.basename(fixture_file))
        open_method, mode = loaddata_command.compression_formats[cmp_fmt]
        fixture = open_method(fixture_file, mode)

        fixture_data = fixture.read()
        objects = {
            'json': json.loads,
            'yaml': yaml.safe_load
        }[ser_fmt](fixture_data)
        return objects
