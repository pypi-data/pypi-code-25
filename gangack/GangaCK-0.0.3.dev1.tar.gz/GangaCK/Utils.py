 
"""
Utils module: Collection of misc functions.
"""

import re
from . import logger
from PythonCK.decorators import memorized

def strfdelta(tdelta):
  """
  Given the timedelta instance, return pretty-print format 
  strictly in hourly unit.

  >>> from datetime import timedelta
  >>> strfdelta(timedelta(days=1))
  '24:00 hrs'

  >>> strfdelta(timedelta(minutes=15))
  ' 0:15 hrs'

  >>> strfdelta(None)
  ''

  """
  if tdelta is None:
    return ''
  hrs,rem = divmod(tdelta.seconds, 3600)
  hrs += 24*tdelta.days
  mins    = rem / 60
  return '{:2}:{:02} hrs'.format(hrs, mins)


@memorized
def validate_intjid(arg):
  """
  Try to cast arg into intjid.
  
  >>> validate_intjid(123)
  123
  
  >>> validate_intjid('123')
  123

  >>> validate_intjid('not_a_number') is None
  True

  >>> validate_intjid(None) is None
  True

  """
  from . import GPI
  if isinstance(arg, int):
    return arg
  if isinstance(arg, basestring):
    try:
      return int(arg)
    except:
      logger.error('Unknown jid: '+arg)
      return
  if isinstance(arg, GPI.Job): # Last, I may not have it
    return arg.fqid
  logger.error('Unknown arg: %r'%arg)
  return

def ignore_closed(s):
  """
  Given string s, return the substituted formed without closed '[CLOSED]' tag. 
  Be careful about additional whitespacing.

  Usage:
      >>> ignore_closed('Hello [CLOSED]')
      'Hello'
      >>> ignore_closed('World[CLOSED]')
      'World'
      >>> ignore_closed('No need to be closed')
      'No need to be closed'

  """
  from GangaCK.Jobtree import TAG_CLOSE
  return s.replace(TAG_CLOSE.strip(), '').strip()

def dictget_ignore_closed(d, key):
  """
  Retrieve value in dict d, whilst ignore the TAG_CLOSE in both key and d.keys()

  Usage:
      >>> dictget_ignore_closed({ 'key[CLOSED]': 'val' }, 'key') 
      'val'
      >>> dictget_ignore_closed({ 'key': 'val' }, 'key [CLOSED]') 
      'val'

  Raises:
    KeyError, when invalid key is given.

  """
  for k,v in d.iteritems():
    # if isinstance(k, basestring):  # If key is string, this is dir (int-key for job)
    if ignore_closed(str(k))==ignore_closed(key):
      return v
  raise KeyError('Missing key: %s'%key)


def expandvars(s, env):
  """
  Helper method to replace envvar in string s from manually-given env dict.

  Usage:
  >>> expandvars( '$DECFILESROOT/options/xxx.py', {'DECFILESROOT': '/some/path'})
  '/some/path/options/xxx.py'

  """
  for var in re.findall(r'(\$\w+)', s):
    varname = var.replace('$', '')
    s = s.replace(var, env.get(varname, var))
  return s


def set_of_int(l):
  """
  - cast iterable of string to int
  - unique by set

  Usage: 
    >>> set_of_int({'2', '3', '1'})
    set([1, 2, 3])
  """
  return { int(x) for x in l }
