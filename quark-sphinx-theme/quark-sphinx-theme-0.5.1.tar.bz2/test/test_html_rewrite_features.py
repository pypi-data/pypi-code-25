# -*- coding: utf-8 -*-
# This file is part of quark-sphinx-theme.
# Copyright (c) 2016, 2017 Felix Krull <f_krull@gmx.de>
# Released under the terms of the BSD license; see LICENSE.

import unittest

from quark_sphinx_theme.ext.html_rewrite._features import (
    create_translator_class, HTMLCompatMixin, BoxesMixin, LiteralBlocksMixin)
from sphinx.writers.html import HTMLTranslator


class TestCreateTranslatorClass(unittest.TestCase):
    CLS = HTMLTranslator

    def test_no_enabled_no_disabled(self):
        cls = create_translator_class(self.CLS, [], [])
        self.assertTrue(issubclass(cls, self.CLS))
        self.assertFalse(issubclass(cls, HTMLCompatMixin))
        self.assertFalse(issubclass(cls, BoxesMixin))
        self.assertFalse(issubclass(cls, LiteralBlocksMixin))

    def test_some_enabled_no_disabled(self):
        cls = create_translator_class(self.CLS, ['compat'], [])
        self.assertTrue(issubclass(cls, self.CLS))
        self.assertTrue(issubclass(cls, HTMLCompatMixin))
        self.assertFalse(issubclass(cls, BoxesMixin))
        self.assertFalse(issubclass(cls, LiteralBlocksMixin))

    def test_no_enabled_some_disabled(self):
        cls = create_translator_class(self.CLS, [], ['boxes', 'literal_blocks'])
        self.assertTrue(issubclass(cls, self.CLS))
        self.assertFalse(issubclass(cls, HTMLCompatMixin))
        self.assertFalse(issubclass(cls, BoxesMixin))
        self.assertFalse(issubclass(cls, LiteralBlocksMixin))

    def test_some_enabled_some_disabled(self):
        cls = create_translator_class(self.CLS, ['compat', 'boxes'],
                                      ['literal_blocks', 'compat'])
        self.assertTrue(issubclass(cls, self.CLS))
        self.assertFalse(issubclass(cls, HTMLCompatMixin))
        self.assertTrue(issubclass(cls, BoxesMixin))
        self.assertFalse(issubclass(cls, LiteralBlocksMixin))


if __name__ == '__main__':
    unittest.main()
