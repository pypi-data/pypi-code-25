"""Nyptune hides a copy of your environment in your Jypyter notebooks so that other people can easily reproduce your work"""

import time
__version__ = '0.0.1.'+str(int(time.time()))

from .magic import *

from IPython import get_ipython
ipy = get_ipython()
if ipy:
    ipy.register_magics(CheckpointMagics)
    print("loaded bitches")