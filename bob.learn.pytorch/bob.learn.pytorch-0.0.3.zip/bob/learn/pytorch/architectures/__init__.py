from .CNN8 import CNN8
from .CASIANet import CASIANet

# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]

