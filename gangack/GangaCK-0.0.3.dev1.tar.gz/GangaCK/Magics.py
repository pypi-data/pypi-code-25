
"""

Collection of custom magic functions.

"""

__all__ = ()

import re
import math
import ColorPrimer
from glob import glob
from . import GPI, logger, _HAS_GANGA
from .Jobtree.OnlineJTWriter import OnlineJTWriter as JT
from PythonCK.itertools import chunks

## Since Ganga 6.1
# Nullify the effect of decorator `register_line_magic` in the case where
# ipython context is not available (e.g., during pytest).
register_line_magic = lambda x: x
if _HAS_GANGA:
  try:
    from IPython import get_ipython
    if get_ipython():
      from IPython.core.magic import register_line_magic
  except ImportError as e: # no IPython available, probably outside GANGA env
    logger.warning(e)


# http://heim.ifi.uio.no/~inf3330/scripting/doc/python/ipython/node6.html

#===============================================================================

def parser_list_int(list_string):
  """
  Try to parse for a list of int. Ignore the unmatches.

  >>> tuple(parser_list_int('123'))
  (123,)
  >>> tuple(parser_list_int('123 456'))
  (123, 456)

  ## Don't accept string
  >>> tuple(parser_list_int('bad'))
  ()

  ## Reject float
  >>> tuple(parser_list_int('12.3'))
  ()

  ## Treat strict int (distinguish from subjobs)
  >>> tuple(parser_list_int('12.0'))
  ()

  ## Exclude bad ones
  >>> tuple(parser_list_int('12 13 14 15.0 16'))
  (12, 13, 14, 16)

  """
  for s in list_string.split():
    try:
      yield int(s)
    except ValueError as e:
      logger.exception(e)
      logger.debug('Ignore: %r'%s)

#-------------------------------------------------------------------------------
# PEEK
#-------------------------------------------------------------------------------

@register_line_magic
def peek(line):
# def peek(self, parameter_s=''):
  """run `peek 1279.0` as shortcut for jobs("1279.0").peek('stdout')"""
  j = GPI.jobs(line)
  if j.status in ('completed', 'failed'):
    try:
      j.peek('stdout')
      j.peek('std.out')
    except:
      logger.debug('magic_peek stdout failed.')
  # Finally, show ls peek at the bottom, if exists
  try:
    j.peek()
  except:
    logger.debug('magic_peek stdout failed.')

#-------------------------------------------------------------------------------
# QUICK - JOBVIEW
#-------------------------------------------------------------------------------

def _print_failed(jid, sj):
  """Try to print useful info for failed subjobs debugging."""
  print '| {0:>4}.{1.id:<4} | {1.backend.actualCE:14} | {1.backend.statusInfo}'.format(jid, sj)

def _qview_single(jobid):
  job     = GPI.jobs(jobid)
  cols    = 120
  lenmax  = len(str(len(job.subjobs)-1))  # Max length of subjobsid, ~3 or 4
  l       = [ColorPrimer.status(sj.status, grey_completed=True).format(sj.id) for sj in job.subjobs]
  N       = int(cols) / (lenmax+1)   # Adjust column width to len of idsubjobs
  N       = int(5*math.floor(float(N)/5))      # Round-down to nearest 5X
  padding = '{0:>%i}'%(lenmax+13) # Offset from len(red)
  header  = "\nJob::#" + ColorPrimer.status(job.status).format(jobid)
  print header, job.name, '::', job.comment
  for sublist in chunks(l, N):
    print " ".join([padding.format(x) for x in sublist])

def _qview_all(*list_jid):
  # If not given, call all non-final
  if not list_jid:
    list_jid = []
    for s in ('submitting', 'submitted', 'running', 'completing'):
      list_jid.extend(GPI.jobs.select(status=s).ids())
  print "\x1b[2J"   # clear line
  for jobid in sorted(list_jid):
    _qview_single(jobid)
  ## Color legends
  print ''  # blank line
  ColorPrimer.print_status_color_legend()
  ## Attempt to see detail of failed subjobs, if any
  queue = []
  for jid in list_jid:
    j = GPI.jobs(jid)
    for sj in j.subjobs.select(status='failed'):
      queue.append([ jid,sj ])
  if queue:
    print 'List of error subjobs::'
    print '|    JID    | actualCE       | statusInfo '
    print '-'*80
    for jid,sj in queue:
      _print_failed(jid, sj)

@register_line_magic
def jv(line):
  """
  Print the list of subjobs id with its respective colors

  Usage:

      jv 975                # Print single job
      jv 1090 1091 1092     # Print mutiple jobs
      jv                    # If no jids, print non-final jobs (e.g., running, submitting, etc.)
  """
  _qview_all(*list(parser_list_int(line)))

#--------------------------------------------------------------

@register_line_magic
def jrm(line):
  """
  rm-equivalent to delete the job from given id.

  Slightly safer with delete-guard, which prevent accidental delete of Job.
  Any Job already put inside jobtree will be guarded by this mechanism, and
  can be deleted either forcefully with command

  Due to compatibility reason, check for jid both in string and int.
  """
  force_delete = False
  if '-f' in line:
    force_delete = True
    line = line.replace('-f', '')
  for intjid in parser_list_int(line):
    loc1 = GPI.jobtree.find(intjid)
    loc2 = GPI.jobtree.find(str(intjid))
    if (loc1 or loc2) and not force_delete: # CAREFUL, use strjid, not intjid
      print 'Safety-delete-guard: please remove job:%r from jobtree first.'%intjid
      print 'Alternatively, provide flag `-f` to force-delete.'
      print 'Location1: %r' % loc1
      print 'Location2: %r' % loc2
    else:
      GPI.jobs(intjid).remove()

#--------------------------------------------------------------

def _parse_index(rawindex):
  """
  Return tuple of indices to be cd by jobtree.

  >>> _parse_index('4')
  (4,)
  >>> _parse_index('4,0,0')
  (4, 0, 0)
  >>> _parse_index('400')
  (4, 0, 0)

  """
  if rawindex=='': # root
    return None
  try:
    x = eval(rawindex)
    if isinstance(x, tuple):
      return x
    else:
      # If it's int, try split by single char
      return tuple(int(i) for i in str(rawindex))
  except Exception, e:
    logger.exception(e)
    raise ValueError('Unknown index: ' + rawindex)

def _parse_cmd(rawcmd):
  """

  >>> _parse_cmd('BANANA')
  Traceback (most recent call last):
  ...
  ValueError: Unknown cmd given: BANANA

  """
  if rawcmd=='':
    return None
  if rawcmd in JT.MAGIC_CMDS:
    return rawcmd
  raise ValueError('Unknown cmd given: '+rawcmd)

def parser_magic_jt(s):
  """
  1. Consecutive numbers (with optional comma)
  2. Optional command text
  3. Optional command's argument(s)

  ## Good args, whitespace doesn't matter

  >>> parser_magic_jt('112 mkdir')
  ((1, 1, 2), 'mkdir', [])
  >>> parser_magic_jt('112   mkdir    ')
  ((1, 1, 2), 'mkdir', [])
  >>> parser_magic_jt('112 mkdir Hello')
  ((1, 1, 2), 'mkdir', ['Hello'])
  >>> parser_magic_jt('112 mkdir s1 s2')
  ((1, 1, 2), 'mkdir', ['s1', 's2'])

  ## Root cmd needs no index

  >>> parser_magic_jt('mkdir')
  (None, 'mkdir', [])
  >>> parser_magic_jt('mkdir hello')
  (None, 'mkdir', ['hello'])

  ## Bad indices

  >>> parser_magic_jt('4 0 0')
  Traceback (most recent call last):
  ...
  ValueError: ...

  >>> parser_magic_jt('40 0')
  Traceback (most recent call last):
  ...
  ValueError: ...

  >>> parser_magic_jt('4,0 0')
  Traceback (most recent call last):
  ...
  ValueError: ...

  >>> parser_magic_jt('40-44')
  Traceback (most recent call last):
  ...
  ValueError: ...


  """
  rawindex, rawcmd, rawargs = re.findall(r'([\d,]*)[ ]*([A-z]*)(.*)', s)[0]
  rawargs = rawargs.strip()
  index   = _parse_index(rawindex)
  cmd     = _parse_cmd(rawcmd)
  args    = rawargs.split(' ') if rawargs else []
  if (not cmd) and (args):
    raise ValueError('Bad input: Arguments with no command: '+s)
  return index, cmd, args

@register_line_magic
def jt(line):
  """

  `JT` is an enhanced approach to Ganga's built-in `jobtree`

  Forget the `jobtree.cd`. Let's do it from the indices.

  .. image:: ../fig_myganga_GPI.jobtree.png

  Usages::
    jt                        # Calling it to see your current tree.
    jt mkdir mydir            # Create new folder at root. Sorted alphabetically.
    jt 0                      # Refering to the `mydir1` directory.
    jt 0 mkdir subdir         # Sub directory can be created.
    jt 00 add 208,209         # Add jobs 208 209 to the `mydir1/subdir` directory.
    jt 0 rename newname       # Rename the `mydir` directory to `newname`

  List of commands:

  - add:
  - clean:
  - close:
  - mkdir:
  - open
  - rename:
  - rm:

  """

  logger.debug(line)
  # Simple no args
  if not line:
    print JT()
    return
  try:
    key, cmd, args = parser_magic_jt(line)
  except Exception, e:
    logger.exception(e)
    logger.warning('Failed to parse magic_jt: '+line)
    return
  # 1. key, !cmd, !args (viewing tree)
  if key and not cmd and not args:
    print JT()[key]
  # 2. key, cmd, ... (full command, regardless args)
  elif key and cmd:
    getattr(JT()[key], cmd)(*args)
  # 3. !key, cmd, ... (command, operating at root)
  elif not key and cmd:
    getattr(JT(), cmd)(*args)
  else:
    raise ValueError('Unknown strategy: %r'%locals())


#===============================================================================

@register_line_magic
def grun(_):
  """
  Run the existing `*ganga*.py` file in that directory, only if there's no conflict.
  """
  l = glob('*ganga*.py')
  if len(l) == 1:
    fname = l[0]
    logger.info("Will run '%s'"%fname)
    ## 6.1.20
    import __main__
    ip = __main__.get_ipython()
    ip.run_line_magic( 'ganga', fname)

    # magic_ganga(l[0])
    # from IPython.iplib import InteractiveShell as IS
    # if hasattr( IS, 'magic_ganga' ): # Pre 6.1 Ganga
    #   IS.magic_ganga(l[0])
    #   return
    # else:  # Execute file manually
    #   IS.magic_run('-i '+l[0])
    #   return

  ## Report in case otherwise
  if len(l)==0:
    logger.info('No *ganga.py matched. Ignore')
  else:
    logger.info('Multiple *ganga.py matched. Ignore')
    for x in l:
      print logger.info(x)
  # IS.magic_ganga(self) # Print more help text.


#===============================================================================

# ? Application Finished With Errors
# ? Exception During Execution

@register_line_magic
def resubmit(line):
  """
  More user-friendly command to resubmit on job with subjobs.

  Note: It may be more natural to extend this functionality to Job instance.
  """

  def run(cmd):
    # print 'DRY-RUN: ', cmd
    GPI.queues.add(cmd)

  def treat_failed_dirac(j):
    aname = j.application._impl._name
    info  = j.backend.statusInfo
    if info == 'Execution Complete':
      cmd = j.backend.reset
    elif info == 'Application Finished Successfully':
      cmd = j.backend.reset
    elif info == 'Pending Requests':
      cmd = j.backend.reset
    elif info == 'Requests done':
      cmd = j.backend.reset
    elif info == 'Exception During Execution':
      ## Try on other CE if it's Gauss, free to roam around
      if aname == 'Gauss':
        j.backend.settings['BannedSites'] = [j.backend.actualCE]
        cmd = j.resubmit
      else:
        ## Simple retry
        cmd = j.backend.reset
    elif info == 'Job stalled: pilot not running':
      j.backend.settings['BannedSites'] = [j.backend.actualCE]
      cmd = j.resubmit
    elif info == 'Job has reached the CPU limit of the queue':
      # ban site used, ignore previous ban
      j.backend.settings['BannedSites'] = [j.backend.actualCE]
      cmd = j.resubmit
    elif 'Stalling for more than' in info:
      j.backend.settings['BannedSites'] = [j.backend.actualCE]
      cmd = j.resubmit
    else: # unknown
      cmd = j.resubmit
    run(cmd)

  for x in line.split():
    x = x.strip() # clean
    j = GPI.jobs(x)
    bname = j.backend._impl._name
    if j.status == 'failed' and not j.subjobs:
      raise NotImplementedError
    ## If it has any failed subjobs, treat only those.
    queue = j.subjobs.select(status='failed')
    if queue:
      if bname == 'Dirac':
        for sj in queue:
          treat_failed_dirac( sj )
      else:
        run(sj.resubmit)
      continue # move to next job in magic queue
    ## Then, when there's no more 'failed' jobs, treat 'completing' Dirac's
    queue = j.subjobs.select(status='completing')
    if queue:
      if bname == 'Dirac':
        for sj in queue:
          run(sj.backend.reset)
      continue # move to next job in magic queue
    ## EXIT
