'''Python bindings for the viral amino-acid alignment program nucamino'''

__version__ = "0.1.0"

NUCAMINO_VERSION = "0.2.0"  # Version of the embedded nucamino binaries.

from .functions import align, align_file  # noqa
from .nucamino import Nucamino  # noqa
