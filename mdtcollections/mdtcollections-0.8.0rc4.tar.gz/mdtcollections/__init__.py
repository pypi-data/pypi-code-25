from .descriptors import *
from .dotdict import DotDict
from .exclusive_list import ExclusiveList
from .named_dict import named_dict

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
