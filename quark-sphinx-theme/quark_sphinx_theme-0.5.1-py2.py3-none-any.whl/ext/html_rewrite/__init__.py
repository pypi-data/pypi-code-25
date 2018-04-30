# -*- coding: utf-8 -*-
# This file is part of quark-sphinx-theme.
# Copyright (c) 2016, 2017 Felix Krull <f_krull@gmx.de>
# Released under the terms of the BSD license; see LICENSE.

from sphinx.writers.html import HTMLTranslator

from ... import __version__
from ..._sphinxversion import sphinx_version_at_least
from ._features import create_translator_class, DEFAULT_FEATURES


def setup_html_translator(app):
    # With the changes in Sphinx 1.6, this hook now works fine for us.
    app.set_translator('html', create_translator_class(
        HTMLTranslator,
        app.config.quark_html_features,
        app.config.quark_html_disabled_features
    ))


# Sphinx < 1.6 compatibility
if sphinx_version_at_least((1, 6)):
    setup_html_translator_compat = setup_html_translator
else:
    from . import _setup_pre16
    setup_html_translator_compat = _setup_pre16.setup_html_translator


def setup(app):
    app.add_config_value('quark_html_features', DEFAULT_FEATURES, 'html')
    app.add_config_value('quark_html_disabled_features', [], 'html')
    app.connect('builder-inited', setup_html_translator_compat)
    return {
        'version': __version__,
        'parallel_read_safe': True,
    }
