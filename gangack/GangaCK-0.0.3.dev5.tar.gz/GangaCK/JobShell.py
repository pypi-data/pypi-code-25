
"""
Helper set of commands to allow interaction with Job instance
in a shell-like manner.
"""

import os
from . import GPI, logger
# from . import *
# from .Decorators import ijob_handler

__all__ = ()

## List of subcommand available in shell
WHITELIST_CMD = 'du', 'head', 'ls'

HEAD_ITEMS = (
  'id',
  'name',
  'comment',
)

HEAD_BACKEND_LSF = (
  'backend.extraopts',
)

HEAD_BACKEND_DIRAC = (
  'backend.id',
  'backend.actualCE',
  'backend.status',
  'backend.settings',
  'backend.statusInfo',
)

HEAD_APP_BENDER = (
  'application.version',
  'application.module.name',
)

# def getattr_rcv(obj, attr, default=None):
#   """
#   Recursive version of hasattr if attr is chained by '.'
#   e.g. Job has backend.settings.
#   """
#   if '.' not in attr:
#     return getattr(obj, attr, default)
#   l = attr.split('.')
#   if hasattr(obj, l[0]):
#     return getattr_rcv(getattr(obj, l[0]), '.'.join(l[1:]))
#   return default

# def print_all_attr(job, listfield):
#   for field in listfield:
#     val = getattr_rcv(job, field)
#     print '{:24} | {:<40}'.format(field, val)

# def head(job):
#   """Return only the interesting fields"""
#   print_all_attr(job, HEAD_ITEMS)
#   if isinstance(job.application, Bender):
#     print_all_attr(job, HEAD_APP_BENDER)
#   if isinstance(job.backend, LSF):
#     print_all_attr(job, HEAD_BACKEND_LSF)

def ls(job):
  raise NotImplementedError
  path = job.outputdir
  if os.path.exists(path):
    for x in sorted(os.listdir(path)):
      print x, os.stat(os.path.join(path,x)).st_size
  for x in job.lfn_list():
    print x

def du(job):
  pass

#==============================================================

def parser_magic_jsh(s):
  """

  >>> parser_magic_jsh('1400')
  ('1400', None, None)

  >>> parser_magic_jsh('1400.1')
  ('1400.1', None, None)

  ## Pseudo shell API
  >>> parser_magic_jsh('1400 ls')
  ('1400', 'ls', [])
  >>> parser_magic_jsh('1400 du -ah')
  ('1400', 'du', ['-ah'])

  # Shellized API
  >>> parser_magic_jsh('1442.11 backend.reset')
  ('1442.11', 'backend.reset', [])

  """

  def try_destring(val):
    try:
      return eval(val)
    except NameError:
      return val

  l = s.strip().split()
  logger.debug(l)
  # Expect the int/float-like as JID
  x = eval(l[0])
  if not isinstance(x, int) and not isinstance(x, float):
    raise ValueError('Unknown key: '+l[0])
  key = l[0]
  if len(l)==1:
    return key, None, None
  cmd   = l[1].strip()
  if len(l)==2:
    return key, cmd, []
  return key, cmd, [try_destring(y) for y in l[2:]]  # Destring into primitive type

def magic_jsh(self, s=''):
  logger.debug(s)
  if not s:
    print 'TOOD: Help'
    return
  try: # Cover both parser and jobs-retrieve
    key, cmd, args = parser_magic_jsh(s)
    logger.debug(str((key, cmd, args)))
    j = GPI.jobs(key)
  except Exception as e:
    logger.warning('Failed to parse magic_jsh: '+s)
    logger.warning(e)
    return
  # Simple call
  if not cmd:
    return j
  # In case of my pseudo-shell methods
  if cmd in WHITELIST_CMD:
    func = globals()[cmd]
    return func(j, *args)
  # In case this is intrinsic GangaAPI
  # attr = getattr_rcv(j, cmd)
  attr = eval('j.'+cmd) # evaluate it as verbatim
  if attr is not None:
    if hasattr(attr, '__call__'):
      return attr(*args) if args else attr()
    else:
      return attr
  # Finally, something undefined
  raise ValueError('Command not found: '+cmd)

