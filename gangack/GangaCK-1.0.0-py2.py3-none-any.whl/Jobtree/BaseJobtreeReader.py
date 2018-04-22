
import os
import re
from string import Formatter  # For Formatter().parse
from abc import ABCMeta, abstractmethod, abstractproperty
from PythonCK.ioutils import size, humansize

from .. import GPI, logger, Utils, ColorPrimer, JobUtils
from . import ROOTDIR, C_BAR
from .Index import Index

## Default jobtree representation format
# Note that the width is obligatory in order to have consistent format of rows
# DEFAULT_TEMPLATE = '{jid!s:>4}-{appchar!b:.1}  {name:<20} {humantime:>10} | {humansize!h:>10} | {lensj:>5} | {comment:50}'
DEFAULT_TEMPLATE = '{fqid!s:>4}-{application_char!b:.1} | {name:<20} {comment:60}' #' {metadata["events"]["input"]:>20}'

## See JobUtils.
# def print_app_shortnames():
#   print 'APP    : [G]auss , [D]aVinci , [B]ender , Gaudi[P]ython'

#-------------------------------------------------------

def format_validate(template):
  raise NotImplementedError

def _dewidth(s):
  """
  >>> _dewidth('.2')
  '--'
  >>> _dewidth('>4')
  '----'
  >>> _dewidth('^7.3')
  '-------'
  >>> _dewidth(None)
  ''
  """
  if not s: return ''
  for n in re.findall(r'(\d+)\D*', s):
    if n:  # first valid number, return it
      return '-'*int(n)
  # return ('{:%s}'%s).format('').replace(' ','-')
  # return '-'*int(re.findall(r'.*(\d+).*',s)[0])

def format_linebreak(template):
  """
  Given a template string, return the new string representing compatible 
  tabular linebreak.

  >>> format_linebreak('|{jid!s:>4}-{appchar!b:.1} | {name:<5} |')
  '|-------|-------|'
  """
  gen = Formatter().parse(template)
  return ''.join( l[0].replace(' ','-')+_dewidth(l[2]) for l in gen )

def flatten_header_text(s):
  """
  >>> flatten_header_text( 'metadata["events"]["input"]' )
  'metadata_events_input'
  """
  return s.replace('[','_').replace(']','').replace('"','').replace("'","")

def format_header(template):
  """
  Given a template string, return the new string representing compatible 
  tabular header row. It made automatically, so the niceness is limited.
  Remove all conversion (which is override by GangaCK's colorization)

  >>> format_header('|{jid:>4}-{appchar!b:.1} | {name:>5} |')
  '| JID-A |  NAME |'
  """
  gen  = Formatter().parse(template)
  keys = ( flatten_header_text(key) for _,key,_,_ in gen if key )
  d    = { key:key.upper() for key in keys }
  template = flatten_header_text(re.sub(r'!\S', '', template)) # Stripout color spec
  return template.format(**d)


#-------------------------------------------------------------------------------

class BaseJobtreeReader(object):
  """
  Base interface for jobtree-wrapper.
  """

  __metaclass__ = ABCMeta
  __slots__ = ( '_index', )

  #------------------#
  # ABSTRACT METHODS #
  #------------------#

  @abstractmethod
  def ls(self, path=ROOTDIR):
    """
    Expect a dict of signature {'folders': list_dirs, 'jobs':list_jobs}.
    TODO: Perhaps it's better to return 2 lists, sorted.
    """
    raise NotImplementedError

  @abstractproperty
  def jobs_all(self):
    """
    Expect a set of all intjids everywhere (not necessary in the tree).
    """
    raise NotImplementedError    

  @abstractmethod
  def job(self, jid):
    """
    Return a GPI.Job 

    If invalid jid is given, it should return None or raise Exception....
    """
    raise NotImplementedError

  #--------#
  # MAGICS #
  #--------#

  def __getitem__(self, indices):
    """Expect indices as tuple of int."""
    logger.debug(indices)
    cwd = ROOTDIR
    for i in indices:  # Dive in step-by-step
      dname = sorted(self.ls(cwd)['folders'])[i-1] # revert to pythonic 0-index
      cwd   = os.path.join( cwd, dname ) 
    self._index = Index(indices, cwd)
    logger.debug(self.cwd)
    return self

  def __str__(self, ignore_closed=False):
    # @reset_cwd_after # See JT.rm. It print itself once before removal, so don't reset yet.
    # with PythonCK.IOUtils.capture() as stdout: 
    # Don't capture, use print is better to have progressive result
    print "\x1b[2J"   # clear line
    print "--------\nJOBTREE\n--------"
    print self.cwd

    ## Print the directory and its contents recursively, start from root
    self.print_dir_recursive(ignore_closed=ignore_closed)
    
    ## Print footer, which only make sense it cwd is root '.'
    if self.cwd == ROOTDIR:
      ## Orphans, if any
      if self.jobs_orphan:
        self.print_orphan_table()
      print # line break
      ColorPrimer.print_status_color_legend() 
      ColorPrimer.print_backend_color_legend()
      print JobUtils.APP_LEGEND
      # print_app_shortnames()
      # self.print_usage()  # Can be slow, careful.
      print 'See `jt help` for usage detail.'
    return ''

  #------------#
  # PROPERTIES #
  #------------#

  @property
  def index(self):
    return getattr(self, '_index', Index()) # Fallback when _index not yet inst
  
  @property
  def cwd(self):
    """Very important marker for most of writer's operations."""
    return self.index.fullpath

  @property
  def jobs(self):
    """Return list of all intjid in this tree, fetch recursively."""
    def _jobs(path):
      d   = self.ls(path)
      lj1 = d['jobs']
      lj2 = [item for childpath in d['folders'] for item in _jobs(os.path.join(path,childpath))]
      return lj1 + lj2
    return sorted([ int(i) for i in _jobs(ROOTDIR)])

  @property  
  def jobs_orphan(self):
    """Return a sorted list of jid of orphaned jobs"""
    s1 = set(self.jobs_all)
    s2 = set(self.jobs)
    return sorted(list(s1-s2))


  #---------#
  # METHODS #
  #---------#

  def print_single_job(self, jid, index=Index(), mixdir=False):
    """
    Wrapper around normal `string.format(dict)` print, with indentation.

    Args:
      mixdir (boolean): Helper flag to indicate whether the job is inside dir 
                        where there's a mixture of jobs+subdirs or not. Provide extra indent.
    """
    indent = index.indent(with_dash=False)
    if indent:  # Only for job inside a tree (not orphans)
      indent += ' ' if not mixdir else C_BAR
    txt = 'JOB NOT FOUND: %r'%jid
    if int(jid) in self.jobs_all:
      j = self.job(jid)
      if j is not None: ## Double proection
        try:
          txt = format(j, DEFAULT_TEMPLATE)
        except ValueError as e:
          logger.warning(DEFAULT_TEMPLATE)
          logger.warning(type(j))
          raise e
    print indent+txt

  def print_dir_recursive(self, index=None, ignore_closed=False):
    ## Use current index if none
    if index is None:
      index = self.index
    ## If dir is close, print only the dirname (index)
    print index
    if not ignore_closed and index.is_close:
      return
    ## If open, print things in more detail
    dat   = self.ls(index.fullpath)
    jids  = sorted(dat['jobs'])
    dirs  = dat['folders']
    mixdir= len(dirs)>0 and len(jids)>0
    ## Print the jobs first
    for jid in jids:
      self.print_single_job(jid, index, mixdir)
    ## Print linebrack between jobs+dirs in case of mixin
    if mixdir:
      print index.indent(with_dash=False)+C_BAR
    ## Finally, loop print the dirs
    is_all_close = len(dirs)>0
    for new_index in index.gen_new_child(dirs):
      self.print_dir_recursive(new_index, ignore_closed=ignore_closed)
      is_all_close &= new_index.is_close
    ## Extra line ending when there're jobs, when it's empty, or all its dir are closed.
    if (len(jids)>0 or len(dirs)==0 or is_all_close):
      print index.indent(with_dash=False)

  def print_orphan_table(self):
    print "\n\nOrphaned jobs::"
    print format_header(DEFAULT_TEMPLATE)
    print format_linebreak(DEFAULT_TEMPLATE)
    for jid in self.jobs_orphan:
      self.print_single_job(jid)
    print 

  def print_usage(self):
    print 'USAGE  :'
    for loc in ( Utils.dir_workspace,  Utils.dir_massstorage ):
      size_total = 0
      for jid in self.jobs_all:
        giveup = (not GPI.jobs(jid).is_final) # Skip if not final
        size_total += size(loc(jid), early_giveup=giveup)
      # size = sum( size(loc(jid)) for jid in self.jobs_all )
      print '{:>9} | {}'.format(humansize(size_total), loc())
