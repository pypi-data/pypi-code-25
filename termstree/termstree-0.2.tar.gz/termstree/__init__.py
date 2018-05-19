from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = '0.0.0+dev'

from .parser import SyntaxError

from .node import Node
from .index import Hit
from .tree import Tree

build = Tree.build
