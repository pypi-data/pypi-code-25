# -*- coding: utf-8 -*-

import os
from .. import ColorPrimer
from . import ROOTDIR, TAG_CLOSE, C_BARDASH, C_BAR, C_EMPTY

class Index(list):
  """
  Abstract object represent the index of each item, as well as its indent representation.

  At its root the index is repr by a single tuple, with following interpretation
  - The len of index is depth inside the tree (len==0 is at root).
  - The value represent its position in that level 
    - First index starts from 1 (not from zero!, in order to have negative value, see below).
    - If value is negative, then it's a last member in that respective level.
  """

  __slots__ = ('_fullpath',)

  def __init__(self, l=tuple(), fullpath=ROOTDIR):
    """

    >>> Index([0])
    Traceback (most recent call last):
    ...
    ValueError: Index starts from 1.

    >>> Index([], 'Some name')
    Traceback (most recent call last):
    ...
    ValueError: Root cannot have name!

    """
    if 0 in l:
      raise ValueError('Index starts from 1.')
    if (not l) and (fullpath is not ROOTDIR):
      raise ValueError('Root cannot have name!')
    super(Index, self).__init__(l)
    self._fullpath = fullpath

  def __abs__(self):
    """
    Return the string (not int!) represents absolute index.
    This is used as anchor to traverse the tree.

    >>> abs( Index([1,2,3]) )
    '123'
    >>> abs( Index([1]))
    '1'
    >>> abs( Index([1,-1]))
    '11'
    >>> abs( Index() )  # root
    ''

    """
    return ''.join([str(abs(i)) for i in self])

  def __repr__(self):
    """
    Representation of Index instance, composed of 3 elements:

    - Indentation, adjust by its hierachy.
    - Integer index, used for navigation.
    - Name of the directory.

    >>> Index([1,-1], 'Mydir')
    |  ├--[11] Mydir

    >>> Index([-1,2], 'Mydir [CLOSED]')
       ├--[12] \033[31;30mMydir [CLOSED]\033[00m

    """
    dname = ColorPrimer.grey.format(self.name) if self.is_close else self.name
    return '{}[{}] {}'.format(self.indent(), abs(self), dname)

  # def __radd__(self, other):
  #   pass

  @property
  def fullpath(self):
    """
    Return index's fullpath (absolute path) from root dir.

    >>> Index().fullpath
    '/'
    >>> Index([1,2], '/dir/name/').fullpath  # Ignore last delimiter
    '/dir/name'

    """
    val = self._fullpath
    if val is not ROOTDIR and val.endswith('/'):
      val = ''.join(list(val)[:-1])
    return val

  @property
  def name(self):
    """
    Return only the last portion of fullpath.

    >>> Index([1], fullpath='/long/path/to/dir').name
    'dir'

    """
    return self.fullpath.split('/')[-1]
  
  @property
  def is_root(self):
    """
    Return True if this index represents root item.

    >>> Index([]).is_root 
    True

    >>> Index([1,2]).is_root
    False

    """
    return len(self)==0

  @property
  def is_close(self):
    """
    Return True if, judging from dirname, it's in close state.
    See TAG_CLOSE.

    >>> Index([1,1], '/some/dirname [CLOSED]').is_close
    True

    >>> Index([1,1], '/some/dirname[CLOSED]').is_close  # Legacy
    True

    >>> Index([1,1], '/some/dirname').is_close
    False

    >>> Index([]).is_close  
    False

    >>> Index([1]).is_close
    False

    """
    if self.is_root:
      return False
    return TAG_CLOSE.strip() in self.fullpath

  @property
  def is_last(self):
    """
    >>> Index([]).is_last # Root is always last
    True

    >>> Index([1]).is_last      
    False

    >>> Index([-2]).is_last     
    True

    >>> Index([1,1]).is_last    
    False

    >>> Index([1,-1]).is_last   
    True

    """
    return True if self.is_root else self[-1]<0

  def gen_new_child(self, names):
    """
    Generate a list of indices with current index as host directory.

    Args:
      names (list): List of string for name of sub directories 

    Yields:
      Index: new Index instance, as sub element

    Usage:
      >>> index = Index()
      >>> for i2 in index.gen_new_child([ 'dir1', 'dir2' ]):
      ...   print i2
      ├--[1] dir1
      ├--[2] dir2

      >>> index = Index([4], fullpath='/the_4th_dir')
      >>> for i2 in index.gen_new_child([ 'dir1', 'dir2', 'dir3' ]):
      ...    print i2
      |  ├--[41] dir1
      |  ├--[42] dir2
      |  ├--[43] dir3

      >>> i2.fullpath
      '/the_4th_dir/dir3'

    """
    for i,name in enumerate(sorted(names)):
      j = i+1  # Start from 1
      if j==len(names):  # is last
        j *= -1
      yield Index(self+[j], os.path.join(self.fullpath,name))


  def indent(self, with_dash=True):
    """Return the indent prefix for given single line."""
    result = []
    for i,index in enumerate(self):
      if i+1==len(self):  # If it's the last character (not last item in dir)
        if with_dash:
          result.append(C_BARDASH)
        else:
          result.append(C_BAR if index>=0 else C_EMPTY)
      else:
        result.append(C_BAR if index>=0 else C_EMPTY)
    return ''.join(result) #.encode('utf-8')

