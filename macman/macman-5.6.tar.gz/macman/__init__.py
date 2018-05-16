
from macman import dialog
from macman import files
from macman import logs
from macman import misc
from macman import munki
from macman import plists
from macman import remoteaccess
from macman import systime
from macman import users
from macman import network
from macman import sysinfo

__version__ = 5.6

# if no log file specified, don't use log
if '__builtin__log' not in locals():
    import __builtin__
    __builtin__.log = None
