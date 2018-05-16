__author__ = 'dpepper'
__version__ = '0.0.1'

"""
Inspired by Facebook's GraphQL graphene library:
https://github.com/graphql-python/graphene/blob/master/graphene/utils/subclass_with_meta.py

Not needed / supported in Python 3
"""

import sys

__all__ = [ 'InitSubclass' ]



if hasattr(object, '__init_subclass__'):
  raise Exception('''
    Not needed, as __init_subclass__ is already
    implemented natively
  ''')

class InitSubclassType(type):
  """Metaclass that implements PEP 487 protocol"""
  def __init__(cls, *args, **kwargs):
    super(InitSubclassType, cls).__init__(*args, **kwargs)

    super_class = super(cls, cls)
    if hasattr(super_class, '__init_subclass__'):
      super_class.__init_subclass__.__func__(cls)


class InitSubclass():
  __metaclass__ = InitSubclassType
