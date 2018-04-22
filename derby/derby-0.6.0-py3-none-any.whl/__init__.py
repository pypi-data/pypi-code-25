from .derby import Roll
from .mods import AddMod, SubMod, MaxMod, MinMod
from .parser import parser
from .__version__ import __version__

def roll(query, verbose=False):
    result = parser.parse(query)
    if verbose:
        return result
    return result.value