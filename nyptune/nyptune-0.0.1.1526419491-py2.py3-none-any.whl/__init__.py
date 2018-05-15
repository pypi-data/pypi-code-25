"""Nyptune hides a copy of your environment in your Jypyter notebooks so that other people can easily reproduce your work"""

import time, os, platform
__version__ = '0.0.1.'+str(int(time.time()))

from .magic import *

# from IPython import get_ipython
# ipy = get_ipython()

def load_ipython_extension(ipy):
    print("loading nyptune")
    ipy.register_magics(CheckpointMagics)
    pid = os.fork()
    if pid == 0:
        if '64' in platform.machine():
            machine = 'amd64'
        else:
            machine = '386'
        name = platform.system().lower()
        ipfs = str(Path(os.path.realpath(__file__)).parent / 'go-ipfs' / 'ipfs')
        
        os.execl(ipfs, "ipfs", "daemon")