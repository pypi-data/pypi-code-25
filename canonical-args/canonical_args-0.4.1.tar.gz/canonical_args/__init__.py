"""
Make top-level imports available.
"""
from __future__ import absolute_import

from .structure import checkspec
from .function import arg_spec, im_arg_spec, register_spec

# pkgutil namespace style packaging
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)



check_args = checkspec

__all__ = ["check_args",
		   "checkspec",
		   "arg_spec",
		   "im_arg_spec",
		   "register_spec"]
