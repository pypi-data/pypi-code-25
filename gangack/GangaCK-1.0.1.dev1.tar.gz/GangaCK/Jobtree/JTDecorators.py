
import functools
from .. import logger
from . import ROOTDIR
from .Index import Index


def forbid_root(method):
  """This decorator will block if command will operate on cwd == root"""
  @functools.wraps(method)
  def wrap(self, *args, **kwargs):
    if self.cwd == ROOTDIR:
      logger.warning("Abort this operation on jobtree's root dir: " + method.__name__)
      return 
    return method(self, *args, **kwargs)
  return wrap  

def reset_cwd_after(method):
  """Using this decorator in class method, it will reset the cwd to root upon exit"""
  @functools.wraps(method)
  def wrap(self, *args, **kwargs):
    result      = method(self, *args, **kwargs)
    self._index = Index(fullpath=ROOTDIR)
    return result
  return wrap

def clean_name(method):
  """
  Make sure the string argument have a safe name. Signature is strictly: func(self, str)
  """
  whitelist = (' ', '.', '_', '-', '+', ':')
  @functools.wraps(method)
  def wrap(self, s):
    if not all(c.isalnum() or c in whitelist for c in s):
      logger.warning('Not clean alphanumeric name, abort: '+s)
      return
    return method(self, str(s))
  return wrap
