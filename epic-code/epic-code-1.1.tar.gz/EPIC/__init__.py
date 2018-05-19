
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

class Unsupported(Exception):
    pass

class NotAnalytic(Exception):
    pass

class DataError(Exception):
    pass

root = __path__[0]
