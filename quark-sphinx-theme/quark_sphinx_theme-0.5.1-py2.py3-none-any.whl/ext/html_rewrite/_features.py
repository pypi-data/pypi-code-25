# -*- coding: utf-8 -*-
# This file is part of quark-sphinx-theme.
# Copyright (c) 2016, 2017 Felix Krull <f_krull@gmx.de>
# Released under the terms of the BSD license; see LICENSE.

from ..._mixin import create_compound_class
from .compat import HTMLCompatMixin
from .boxes import BoxesMixin
from .literal_blocks import LiteralBlocksMixin


# List so it has a stable order. Descending order of precedence.
FEATURE_CLASSES = [
    ('boxes', BoxesMixin),
    ('literal_blocks', LiteralBlocksMixin),
    ('compat', HTMLCompatMixin),
]
ALL_FEATURES = [f[0] for f in FEATURE_CLASSES]
# This may change.
DEFAULT_FEATURES = ALL_FEATURES


def create_translator_class(cls, enabled_features, disabled_features):
    return create_compound_class(cls, (
        mixin for feature, mixin in FEATURE_CLASSES
        if feature in enabled_features and feature not in disabled_features
    ))
