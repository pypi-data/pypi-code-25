from os.path import dirname, basename, isfile
import glob
from setuptools import find_packages

__all__ = find_packages(dirname(__file__))

# modules = [basename(f)[:-3] for f in glob.glob(dirname(__file__)+"/*.py") if isfile(f) and not f.endswith('__init__.py')]
# __all__.extend(modules)