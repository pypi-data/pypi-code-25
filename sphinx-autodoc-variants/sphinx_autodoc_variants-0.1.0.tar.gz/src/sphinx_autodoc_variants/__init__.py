"""
    sphinx_autodoc_variants
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    An extension for sphinx to allow automatic documentation of
    `variants` functions.

    :copyright: Copyright 2017 by Paul Ganssle <paul@ganssle.io>
    :license: Apache 2.0, see LICENSE for details.
"""

from .variant_autodoc import PrimaryFunctionDocumenter
from .variant_autodoc import PrimaryMethodDocumenter
from .variant_autodoc import VariantFunctionDocumenter
from .variant_autodoc import VariantMethodDocumenter

from sphinx.domains.python import PythonDomain

if False:
    # For type annotations
    from typing import Any, Dict, Text  # noqa, pragma:nocover
    from sphinx.application import Sphinx  # noqa, pragma:nocover

try:
    from ._version import version as __version__
except ImportError:
    __version__ = 'unknown'     # str


def setup(app):
    # type: (Sphinx) -> Dict[Text, Any]
    app.add_autodocumenter(PrimaryFunctionDocumenter)
    app.add_autodocumenter(VariantFunctionDocumenter)
    app.add_autodocumenter(PrimaryMethodDocumenter)
    app.add_autodocumenter(VariantMethodDocumenter)

    return {'version': __version__, 'parallel_read_safe': True}
