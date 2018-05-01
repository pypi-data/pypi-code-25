# Copyright (C) 2017 Pluralsight LLC

import unittest
import six
from six import BytesIO as StringIO
# try:
#   from cStringIO import StringIO
# except ImportError:
#   from StringIO import StringIO
try:
    type(unicode)
except NameError:
    unicode = str

import json
import spavro.schema
import spavro.io

from spavro.io import FastDatumWriter


class TestMoreIo(unittest.TestCase):
    def setUp(self):
        self.fdw = FastDatumWriter()
        self.sdw = SlowDatumWriter()

# name, schema, data
cases = (
("null_and_list_in_union", [{"type": "array", "items": "string"}, "null"], None)
)


def create_case(schema, datum):
    def compare_old_and_new(self):
        buffer = StringIO()
        encoder = spavro.io.FastBinaryEncoder(fastbuff)
        write_schema = spavro.schema.parse(json.dumps(schema))
        for i in range(10):
            self.fdw.write_data(write_schema, datum, fastencoder)
            self.sdw.write_data(write_schema, datum, slowencoder)
        self.assertEqual(fastbuff.getvalue(), slowbuff.getvalue())
    return compare_old_and_new


def make_cases():
    for name, schema, datum in cases:
        test_method = create_case(schema, datum)
        test_method.__name__ = 'test_write_old_vs_new_{}'.format(name)
        setattr(TestOldVsNew, test_method.__name__, test_method)

make_cases()
