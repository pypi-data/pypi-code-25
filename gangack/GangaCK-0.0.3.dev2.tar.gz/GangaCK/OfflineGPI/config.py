"""

Mimic `config` interface, read .gangarc file directly.

USE WITH CARE!

Disclaimer: It can be inaccurate, especially for value not set by user.
The genuine mechanism will be able to handle these default values more 
correctly. 

TODO: Use me
https://pytest.org/latest/monkeypatch.html

Note: $GANGA_CONFIG_FILE can point to custom location, default to ~/.gangarc

Note: $GANGADIR can override GPI.config.Configuration.gangadir,
      This is mainly used by Jobtree mechanism outside Gaudi framework.

"""

import os
import re

#-------------------------------------------------------------------------------

def gangarc_path(raise_exception=True):
  """
  Locate the fullpath to user's config file.
  Default to home's ~/.gangarc.
  Overridable by GANGA_CONFIG_FILE.

  >>> _ = getfixture('res_gangarc')
  >>> gangarc_path()
  'tests/res/gangarc_test'

  """
  path = os.path.expanduser('~/.gangarc')
  if 'GANGA_CONFIG_FILE' in os.environ:
    path = os.environ['GANGA_CONFIG_FILE']
  if not os.path.exists(path):
    if raise_exception:
      raise IOError('Missing gangarc file: '+path)
  return path

def gangarc_raw():
  """Helper method to return entire content of .gangarc"""
  with open(gangarc_path()) as fin:
    return fin.read()

# @memorized  # Not good for testing mulitple gangarc
def gangarc_section(section):
  r"""
  Return entire raw string of given section.
  
  >>> _ = getfixture('res_gangarc')
  >>> gangarc_section('TESTSECTION1')
  'key1 = val1\nkey2 = val2\n#key2 = val2old\n# key3 = val3'

  >>> gangarc_section('BAD')
  Traceback (most recent call last):
  ...
  ValueError: Unknown section: 'BAD'

  """
  dat = gangarc_raw()
  res = re.findall(r'\[%s\](.*?)\[\w+\]'%section, dat, re.DOTALL)
  if not res:
    raise ValueError('Unknown section: %r'%section)
  return res[0].strip()

# @memorized
def gangarc_getraw(section, key):
  """
  
  >>> _ = getfixture('res_gangarc')
  
  >>> gangarc_getraw('TESTSECTION1', 'key1')
  'val1'

  >>> gangarc_getraw('TESTSECTION1', 'BAD')
  Traceback (most recent call last):
  ...
  KeyError: 'Failed to determine request section:key. TESTSECTION1.BAD'

  """
  dat   = gangarc_section(section)
  lines = re.findall(r'(.*)'+key+r'.*=(.*)', dat)
  if len(lines)==1:
    return lines[0][1].strip()
  lines = [ l for l in lines if '#' not in l[0] ]
  if len(lines)==1:
    return lines[0][1].strip()
  raise KeyError('Failed to determine request section:key. %s.%s'%(section,key))

#-------------------------------------------------------------------------------

class Config(object):

  def __getattr__(self, key):
    """

    >>> _ = getfixture('res_gangarc')
    >>> config = Config()
    >>> config.TESTSECTION1.key1
    'val1'
    >>> config.TESTSECTION1.key2
    'val2'
    >>> config.Configuration.Batch
    'LSF'
    >>> config.DIRAC.MaxDiracBulkJobs
    '2000'

    """
    return Section(key)

class Section(object):

  def __init__(self, name):
    self._name = name

  def __getattr__(self, key):
    """

    ## For 'gangadir', Prefer envvar
    >>> getfixture('testuser')
    >>> getfixture('res_gangarc')
    >>> Config().Configuration.gangadir
    '/home/testuser/gangadir'
    
    >> monkeypatch.setenv('GANGADIR', '/some/path')
    >> Config().Configuration.gangadir
    '/some/path'

    """

    ## Override: gangadir
    if (self._name,key) == ('Configuration', 'gangadir'):
      if 'GANGADIR' in os.environ:
        return os.environ['GANGADIR']
    ## Continue like normal
    try:
      val = gangarc_getraw(self._name, key)
      return val
    except IOError, e:
      ## Fallback for Configuration.user
      if (self._name,key) == ('Configuration', 'user'):
        return os.environ['USER']
      ## No fallback, raise
      raise e
