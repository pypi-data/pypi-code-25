
"""

Provide patches for GangaLHCb.Lib.Applications classes.

"""

import re
import Utils
from . import GPI, logger
from PythonCK.decorators import cache_to_file

# def new_app_optsfile( oldsetter ):
#   """
#   Helper method to allow setting `optsfile` attribute to app enabling envvar.
#   It returns new property descriptor with wrapped over old one.
#   """
#   def fget( self ):
#     return self._impl.optsfile
#   def fset( self, opts ):
#     logger.info('Loading env')
#     env = self.getenv()
#     oldsetter( self, [ Utils.expandvars(opt,env) for opt in opts ])
#   return property( fget, fset )
## Patching::
# GPI.Gauss.optsfile = new_app_optsfile( GPI.Gauss.optsfile )

"""
NOTE: These will NOT WORKS if optsfile is set inside constructor!!
Consider this as experimental!
"""

def _getenv(app):
  """
  Helper method to cache the `getenv` method of application. Using closure to 
  properly define the cache
  All key are string to be safely hashable.
  """
  @cache_to_file
  def _getenv_wrap( clsname, version, platform ):
    app = getattr( GPI, clsname )()
    app.version  = version
    app.platform = platform
    logger.info('Caching env: %s-%s-%s' % ( clsname, version, platform ))
    return app.getenv()
  return _getenv_wrap( app._impl._name, app.version, app.platform )

def _app_optsfile_fget( self ):
  return self._impl.optsfile

def _app_optsfile_fset( self, opts ):
  ## Wrap in container in case of string
  if isinstance(opts, basestring):
    opts = [opts]
  ## Prep
  env = _getenv( self )
  self._impl.optsfile = []  # clear()
  self._impl.optsfile.extend([ Utils.expandvars(opt,env) for opt in opts ])

app_optsfile = property(_app_optsfile_fget, _app_optsfile_fset)

#===============================================================================

@cache_to_file
def Gauss__nickname( decid ):
  """
  Helper method to return nickname of given DECFILE id.

  Args:
    decid (str/int): 8-digits DecFile ID.

  """
  app   = GPI.Gauss()  # Pickup latest definition
  env   = _getenv(app)
  fpath = '$DECFILESROOT/options/%s.py'%decid 
  ## 1. Read the parsed python file.
  with open(Utils.expandvars(fpath, env)) as fin:
    dat = fin.read()
  ## 2. Read the actual decfile.
  fpath = re.findall(r'UserDecayFile = "(\S+)"', dat)[0]
  with open(Utils.expandvars(fpath, env)) as fin:
    dat = fin.read()
  logger.debug(dat)
  return re.findall(r'NickName:(.*)', dat)[0].strip()

#===============================================================================

# def DaVinci__events_fget( self ):
#   raise NotImplementedError('Sorry...')
# def DaVinci__events_fset( self, val ):
#   """
#   Helper method to provide similar interface of `Bender.events` to DaVinci 
#   to quickly override event number to DaVinci() app.

#   >> app = DaVinci()
#   >> app.events = 1E3  # cast to int
#   """
#   val = int(val)
#   self.extraopts += "from Configurables import DaVinci; DaVinci().EvtMax = %i"%val
# DaVinci__events = property( DaVinci__events_fget, DaVinci__events_fset )
