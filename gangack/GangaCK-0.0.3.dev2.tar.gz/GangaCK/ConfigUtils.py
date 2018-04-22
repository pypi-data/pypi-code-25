"""

All the important Utils, to be loaded after config, but probably
be used by many things after this...

"""

import os
import Utils
from PythonCK.decorators import memorized

## Cached version
@memorized
def _dir_workspace():
  from . import GPI  # Prefer late-import
  return os.path.join(GPI.config.Configuration.gangadir, 'workspace', GPI.config.Configuration.user, 'LocalXML')

def dir_workspace(jid=None):
  """
  Return path to workspace's directory, dive to specific dir if jid is given.

  Usage:
  
    >>> getfixture('testuser'); getfixture('res_gangarc')
    >>> dir_workspace()
    '/home/testuser/gangadir/workspace/testuser/LocalXML'
    >>> dir_workspace(42)
    '/home/testuser/gangadir/workspace/testuser/LocalXML/42'
    >>> dir_workspace('42')
    '/home/testuser/gangadir/workspace/testuser/LocalXML/42'
    >>> dir_workspace('42.12345')
    '/home/testuser/gangadir/workspace/testuser/LocalXML/42/12345'
    >>> dir_workspace('42/12345')
    '/home/testuser/gangadir/workspace/testuser/LocalXML/42/12345'

  """

  path = _dir_workspace()
  if jid is None:
    return path
  return os.path.join(path, str(jid).replace('.','/'))

## Cached version
@memorized
def _dir_repository():
  from . import GPI
  return os.path.join(GPI.config.Configuration.gangadir, 'repository', GPI.config.Configuration.user, 'LocalXML/6.0')


def dir_repository(jid=None):
  """
  Return path to repository's directory.
  Remark on the thousand-prefix.

  Usage:

    >>> getfixture('testuser'); getfixture('res_gangarc')
    >>> dir_repository()
    '/home/testuser/gangadir/repository/testuser/LocalXML/6.0'
    >>> dir_repository(42)
    '/home/testuser/gangadir/repository/testuser/LocalXML/6.0/jobs/0xxx/42'
    >>> dir_repository('42')
    '/home/testuser/gangadir/repository/testuser/LocalXML/6.0/jobs/0xxx/42'
    >>> dir_repository(2500)
    '/home/testuser/gangadir/repository/testuser/LocalXML/6.0/jobs/2xxx/2500'
    >>> dir_repository('2500.42')
    '/home/testuser/gangadir/repository/testuser/LocalXML/6.0/jobs/2xxx/2500/42'
    >>> dir_repository('2500/42')
    '/home/testuser/gangadir/repository/testuser/LocalXML/6.0/jobs/2xxx/2500/42'

  """

  path = _dir_repository()
  if jid is None:
    return path 
  subdir = str(jid).replace('.','/')
  prefix = int(str(jid).split('.')[0].split('/')[0])/1000
  path  += '/jobs/{}xxx/{}'.format( prefix, subdir )
  return path

def dir_massstorage(jid=None):
  """
  Return path to mass-storage directory

  Usage:
    >>> getfixture('testuser')
    >>> dir_massstorage(250)
    '/storage/testuser/250'
  """
  from . import GPI
  path = GPI.config.Output.MassStorageFile['uploadOptions']['path']
  # except Exception, e:
  #   logger.warning('Pre-eval: %r' % GPI.config.Output.MassStorageFile)
  #   logger.exception(e)
  if jid:
    path = os.path.join(path, str(jid))
  return path

def dirnames(path):
  """
  Given a path, return set of all directories' (relative) names in that path.
  Double check if directory exists or not.

  >>> monkeypatch.setattr('os.listdir'   , lambda x: ['d1', 'd2', 'd3'])
  >>> monkeypatch.setattr('os.path.isdir', lambda x: True)
  
  >>> dirnames('some/path/to/directory')
  ['d1', 'd2', 'd3']
  
  """
  path = os.path.expandvars(path)
  dnames = next(os.walk(path))[1]  # Slightly less verbose that os.listdir of same speed
  return sorted(dnames)


def jids_repository():
  """
  Return set of all jobs' ids (INT) in the repository directory.  
  """
  rpath   = dir_repository()
  queue1  = ( d for d in dirnames(os.path.join(rpath,'jobs')))
  queue2  = ( d2 for d1 in queue1 for d2 in dirnames(os.path.join(rpath,'jobs',d1 )) )
  return Utils.set_of_int(queue2)

def jids_workspace():
  """Return set of jid (INT) in workspace."""
  return Utils.set_of_int(dirnames(dir_workspace()))

def jids_massstorage():
  return Utils.set_of_int(dirnames(dir_massstorage()))
