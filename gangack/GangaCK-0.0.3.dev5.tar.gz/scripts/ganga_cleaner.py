#!/usr/bin/env python

"""
================================ GANGA CLEANER ================================

Complete all-in-one script for tidying your ganga environment.

Feature

- dry-run by default (Report potential deletable files). 
  The script will NEVER delete any files on its own.
  The user always have to delete files themselve. This encourages the user to 
  have the final check, and makes script simple, robust, and easily scalable.

- For each module, the suggestion of cleanup command is provided.

- Check the repo specified in `MassStorageFile` for orphans.
  - Orphans compared against workspace+repository directory

- Check jid discrepancy between 'gangadir/repository' and 'gangadir/workspace'




> Clean the formatting of job tree
> Check the repo specified in `LFN` for orphans.
> Check 'gangadir/shared/{username}/' for orphans


Caveat (for now, will move to flag if possible):
- Required .gangarc at $HOME/.gangarc
- Required $GANDADIR

===============================================================================
"""

import os
import subprocess
from glob import glob

from PythonCK import logger
from PythonCK.ioutils import size, humansize
from PythonCK.itertools import chunks
from PythonCK.decorators import memorized
logger.setLevel(50)
from GangaCK import ConfigUtils
logger.setLevel(logger.INFO)
logger.info('Quietly force-imported GangaCK')

#-------------------------------------------------------------------------------

## default to be used
GANDADIR_EOS = os.path.expandvars('$EOS_HOME/ganga')

from multiprocessing import Pool

#-------------------------------------------------------------------------------

def print_list_int(l=None):
  """
  Custom printer for list of integer
  - Unique (set)
  - Sorted.
  - Formatted to 4-digits width.
  - Splitted to chunk for long list.
  - Show (none) when list is empty.
  """
  ## retrieve generator, null check, 
  l = [ x for x in l if x is not None ]
  if not l:
    print '(None)'
    print
    return
  for l2 in chunks(sorted(list(set(l))), 20):
    for x in l2:
      print '%4i'%x,
    print
  print

@memorized
def jids_eos():
  """
  Simply list all jids on default gangadir on user's eos.
  Need a working token.

  TODO: Share code with xmlmerge.
  """
  args    = [ 'eos', 'ls', GANDADIR_EOS ]
  stdout  = subprocess.check_output( args )
  return (int(s.split('h')[-1]) for s in stdout.split()) # kill weird char.

def pool_map_jids(f):
  """
  Helper to run function f over all jids, using pool. Return res from Pool.map
  """
  return Pool(10).map( f, ConfigUtils.jids_workspace() )

#===============================================================================

def compare_workspace_repository():
  """
  Compare the list of jids present/absent between both dir.
  """
  lw = ConfigUtils.jids_workspace()
  ls = ConfigUtils.jids_repository()
  print '## JID In workspace only, not in repodir:'
  print_list_int(lw-ls)
  print '## JID In repository only, not in wdir:'
  print_list_int(ls-lw)

def clean_mass_storage():
  print
  print '---------------------------------------'
  print 'Fetching MassStorage path in .gangarc'
  print '---------------------------------------\n'

  path = ConfigUtils.dir_massstorage()
  print 'Path: %s'%path
  if not path:
    return
  ## Use set to find orphans
  # lall    = Utils.intset(Utils.dirnames(path))
  lall    = ConfigUtils.jids_massstorage()
  lw      = ConfigUtils.jids_workspace()
  lp      = ConfigUtils.jids_repository()
  orphans = sorted(list( lall - lw - lp ))
  print_list_int(orphans)
  ## Abort calculation 
  if not orphans:
    return
  # print 'Found these orphans: (%d dirs)' % len(orphans)
  ## Try to return total storage usage
  print '\n(Calculating deletable disk usage, please wait)'
  total_size = 0
  for jid in orphans:
    val = size(os.path.join(path, str(jid)))
    total_size += val
    print 'JID', jid, 'size: ', val, ' '*20, '\r',
  print ' '*40, '\r',
  print 'Deletable space: %s' % humansize(total_size)
  print 

def clean_eos():
  """
  Report the list of jids on user's EOS dir which does not appear in repo/wrk.
  """
  l0      = set(jids_eos())
  lw      = ConfigUtils.jids_workspace()
  lp      = ConfigUtils.jids_repository()
  orphans = sorted(list( l0 - lw - lp ))

  print '## Check EOS orphans dirs:', GANDADIR_EOS
  print '> eos rm -r ...'
  print_list_int(orphans)

#===============================================================================

def f_check_workspace_residual_hadd(jid):
  """
  Return
  - True : Has residual, has merged result
  - False: Has residual, no merged result
  - None : No residual
  """
  path    = ConfigUtils.dir_workspace(jid)
  opath   = os.path.join( path, 'output' )
  if os.path.exists(opath):
    ofiles = [ fname for fname in os.listdir(opath) if fname.endswith('.root') ]
  else:
    ofiles = []

  ## 1. Use glob
  res = glob(os.path.join(path, '*/output/*.root'))
  if res:
    fnames = { os.path.split(x)[-1] for x in res }
    for fname in fnames:
      # separate whether there's respective file in output or not
      # care for any first result found.
      return fname in ofiles

def check_workspace_residual_hadd():
  """
  Try to report the case where job with subjobs has merged output root and
  the children root files can possibly be deleted.

  Do a quick search by, grepping for */output/*.root.
  The non-null existence means it's probable so.
  """
  print "## Check residual hadd"

  queue   = pool_map_jids( f_check_workspace_residual_hadd )
  queue1  = []
  queue2  = []
  for res in queue:
    if res is True:
      queue1.add(res)
    if res is False:
      queue2.add(res)

  print "## Check residual hadd with merged file in ./output."
  print '> rm */output/*.root'
  print_list_int(queue1)
  
  print "## Check residual hadd with no file in ./output."
  print '> hadd XXX.root */output/XXX.root'
  print_list_int(queue2)

#===============================================================================

def f_check_workspace_unmerged_summaryxml(jid):
  path = ConfigUtils.dir_workspace(jid)
  child_has   = bool(glob(os.path.join(path, '*/output/summary.xml')))
  parent_has  = bool(glob(os.path.join(path, 'output/summary.xml')))
  if child_has and not parent_has:
    return jid

def check_workspace_unmerged_summaryxml():
  print '## Check possible unmerged summary.xml'
  print '> xmlmerge.py'
  queue = pool_map_jids( f_check_workspace_unmerged_summaryxml )
  print_list_int(queue)

#===============================================================================

def f_check_worspace_archivable(jid):
  path = ConfigUtils.dir_workspace(jid)
  if any(x.isdigit() for x in os.listdir(path)):
    return jid

def check_worspace_archivable():
  """
  Report the job in workspace with subdirectories of subjobs. 
  Recommending archival for smoother disk IO.
  """
  print '## Check possible workspace job for archive'
  print "> tar -Jcvf data.tar.xz --exclude='./output' ."
  queue = pool_map_jids( f_check_worspace_archivable )
  print_list_int(queue)

#===============================================================================

# def check_gauss_outputs():
#   """
#   Most large output files from Gauss-job (*.xgen, *.gen, *.sim) can be deleted
#   once they're processed to full sim.

#   # TODO: Decide the mechanics to determine job's appname starts from JID. 
#   """
#   list_jids_eos = jids_eos()
#   for jid in ConfigUtils.jids_repository():
#     pass

#===============================================================================

WDIR_WHITELIST = [ 
  'tuple.root',
  'output.lhe',
  # remove me later
  'tuple_partial.root',
  'tuple_rev.root',
]

## Cached list of files on EOS
## TODO: Shouldn't be on the 
EOS_FILES = []

def f_check_wdir_push_eos(jid):
  def valid(fpath):
    """Return True if this file should be checked on EOS."""
    return any( w in fpath for w in WDIR_WHITELIST )
  #
  path = ConfigUtils.dir_workspace(jid)
  for fpath in glob(os.path.join( path, 'output/*' )):
    fname = os.path.split(fpath)[-1]
    if valid(fpath):
      eospath = os.path.join( GANDADIR_EOS, str(jid), fname )
      if eospath not in EOS_FILES:
        return jid 

def check_wdir_push_eos():
  """
  Report the output file only on wdir but not on EOS, suggest pushing for backup.
  """
  print '## Check data files in {jid}/output not existed on EOS. Recommending backup.'
  print '> eoscp {src} {target}'

  ## Saving cache, used by child process
  global EOS_FILES
  EOS_FILES = subprocess.check_output(['eos','find', GANDADIR_EOS]) 
  ## Actual run
  queue = pool_map_jids( f_check_wdir_push_eos )
  print_list_int(queue)


#===============================================================================

def main():
  print __doc__
  compare_workspace_repository()
  # clean_mass_storage()
  clean_eos()
  # check_workspace_residual_hadd()
  check_workspace_unmerged_summaryxml()
  check_wdir_push_eos()
  check_worspace_archivable() # last


if __name__ == '__main__':
  main()

