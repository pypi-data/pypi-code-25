# -*- coding: utf-8 -*-
# This file is part of quark-sphinx-theme.
# Copyright (c) 2017 Felix Krull <f_krull@gmx.de>
# Released under the terms of the BSD license; see LICENSE.

import unittest
try:
    from unittest import mock
except ImportError:
    import mock

from quark_sphinx_theme import _sphinxversion


class _VersionInfo:
    def __init__(self, version_info):
        self.version_info = version_info


class TestSphinxVersionAtLeast(unittest.TestCase):
    @mock.patch('quark_sphinx_theme._sphinxversion.sphinx', object())
    def test_should_return_false_if_missing_sphinx_version_info(self):
        self.assertFalse(_sphinxversion.sphinx_version_at_least((1, 0)))
        self.assertFalse(_sphinxversion.sphinx_version_at_least((1, 6)))
        self.assertFalse(_sphinxversion.sphinx_version_at_least((2, 0)))

    @mock.patch('quark_sphinx_theme._sphinxversion.sphinx',
                _VersionInfo((1, 6, 0, 1)))
    def test_should_return_false_if_actual_version_lower(self):
        self.assertFalse(_sphinxversion.sphinx_version_at_least((1, 7)))
        self.assertFalse(_sphinxversion.sphinx_version_at_least((2, 0)))
        self.assertFalse(_sphinxversion.sphinx_version_at_least((3, 8)))

    @mock.patch('quark_sphinx_theme._sphinxversion.sphinx',
                _VersionInfo((2, 1, 7)))
    def test_should_return_true_if_actual_version_greater(self):
        self.assertTrue(_sphinxversion.sphinx_version_at_least((1, 1)))
        self.assertTrue(_sphinxversion.sphinx_version_at_least((1, 6)))
        self.assertTrue(_sphinxversion.sphinx_version_at_least((2, 0)))


if __name__ == '__main__':
    unittest.main()
