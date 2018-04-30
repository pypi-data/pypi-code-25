# -*- coding: utf-8 -*-
# This file is part of quark-sphinx-theme.
# Copyright (c) 2017 Felix Krull <f_krull@gmx.de>
# Released under the terms of the BSD license; see LICENSE.

import sphinx


def sphinx_version_at_least(version):
    if hasattr(sphinx, 'version_info'):
        sphinx_version = sphinx.version_info[:2]
    else:
        sphinx_version = (0, 0)
    return sphinx_version >= version
