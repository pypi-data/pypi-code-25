# -*- coding: utf-8 -*-
# This file is part of quark-sphinx-theme.
# Copyright (c) 2016, 2017 Felix Krull <f_krull@gmx.de>
# Released under the terms of the BSD license; see LICENSE.

from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.writers.html import HTMLTranslator

from ._features import create_translator_class


def setup_html_translator(app):
    # So this is a bit hacky; the "proper" way would be to use the new
    # app.set_translator function added in Sphinx 1.3, but that's much more
    # awkward because
    #  a) it's new in 1.3
    #  b) there's no extension hook after the configuration is loaded, but
    #     before the builder is created; meaning we would have to replace the
    #     translator class much more broadly and sort out any settings later.
    from sphinx.writers.html import SmartyPantsHTMLTranslator
    KNOWN_TRANSLATORS = [
        HTMLTranslator,
        SmartyPantsHTMLTranslator
    ]

    cls = app.builder.translator_class
    is_html = isinstance(app.builder, StandaloneHTMLBuilder)
    if is_html and cls in KNOWN_TRANSLATORS:
        app.builder.translator_class = create_translator_class(
            cls,
            app.config.quark_html_features,
            app.config.quark_html_disabled_features
        )
