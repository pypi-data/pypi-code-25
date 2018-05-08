from __future__ import absolute_import
from __future__ import print_function

import six

from unittest import TestCase

if six.PY2:
    TestCase.assertRaisesRegex = TestCase.assertRaisesRegexp
    TestCase.assertRegex = TestCase.assertRegexpMatches
