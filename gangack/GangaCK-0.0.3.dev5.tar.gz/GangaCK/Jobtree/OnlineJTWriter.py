
import os
from .. import GPI, logger, Utils
from . import ROOTDIR, TAG_CLOSE
from . import __doc__ as doc
from .OnlineJobtreeReader import QuickOnlineJobtreeReader
from .JTDecorators import reset_cwd_after, forbid_root, clean_name

## Handle
jt = GPI.jobtree

#===============================================================================

class OnlineJTWriter(QuickOnlineJobtreeReader):

  __slots__ = []

  ## List of available commands for magic_jt
  ## Manual first, so I can gradually rollout features
  MAGIC_CMDS = ('add', 'clean', 'close', 'find', 'mkdir', 'open', 'rm', 'rename')

  def __init__(self):
    jt.cd()

  @reset_cwd_after
  @forbid_root
  def add(self, *list_jid):
    """
    Add the list of jobs to current directory.
    """
    for jid in list_jid:
      ## Recheck casting into ints
      jid = Utils.validate_intjid(jid)
      if not jid:
        continue
      ## Abort if it's not existed
      if jid not in GPI.jobs.ids():
        logger.warning('JID not existed, ignore: %d'%jid)
        continue
      ## Finally, execute
      jt.add(GPI.jobs(jid), self.cwd)
      logger.info("Added job-%i into directory: %s" % (jid, self.cwd))

  @reset_cwd_after
  def find(self, *args):
    """
    Delegate the work to native jobtree.
    """
    for arg in args:
      arg = str(arg)
      logger.info('Find: '+arg)
      print jt.find(arg)

  @reset_cwd_after
  @clean_name
  def mkdir(self, *list_name):
    """
    Create the new dir in cwd.
    """
    for name in list_name:
      jt.mkdir(os.path.join(self.cwd, name))
      logger.info("mkdir '%s' into directory: %s" % (name, self.cwd))

  @reset_cwd_after
  def _mv(self, destroot=ROOTDIR, src=None):
    """
    Move the srcdir into the destroot. Non-trivial operation.
    """
    if src is None:
      src = self.cwd
    logger.debug("Moving: '%s' into '%s'" % (src, destroot))
    dest = destroot+'/'+src.split('/')[-1]
    if jt.exists(dest) and jt.ls(src)==jt.ls(dest):
      logger.warning( "mv itself. Abort" )
      print jt.ls(src)
      print jt.ls(dest)      
      return
    logger.debug("mv mkdir: "+dest)
    jt.mkdir(dest)
    # Add the jobs from src to dest
    jt.add(jt.getjobs(src), dest)
    # Do mv on all subdir
    for dname in jt.listdirs(src):
      self._mv(destroot=dest, src=src+'/'+dname)
    jt.rm(src)
    logger.debug( "mv removed: "+src)

  @reset_cwd_after
  @forbid_root
  def rename(self, newname):
    """
    Rename the current cwd directory.
    """
    assert '/' not in newname, "Cannot do rename with level change."
    l_dest     = self.cwd.split('/')
    l_dest[-1] = newname
    dest       = '/'.join(l_dest)
    src        = self.cwd
    jt.mkdir(dest)
    jt.add(jt.getjobs(src), dest)
    for dname in jt.listdirs(src):
      self._mv(destroot=dest, src=src+'/'+dname)
    jt.rm(src)  # Delete itself
    logger.info("Renamed : %s" % src)
    logger.info("    --> : %s" % dest)

  @reset_cwd_after
  @forbid_root
  def clear(self):
    """
    Clear all contents (jobs/dirs) inside this directory.
    """
    raise NotImplementedError

  @reset_cwd_after
  @forbid_root
  def rm(self, *list_jid):
    """
    Remove given jid from the current cwd.
    """
    # Remove the entire directory, ask confirmation
    logger.debug(str(list_jid))
    if not list_jid:
      print "This requested directory will be removed::"
      print self
      x = raw_input('\nConfirm removing this jobtree dir (the jobs themselves are not affected) ?? Y/[n] ')
      if x=='Y':
        logger.debug("Pending removal: " + self.cwd)
        jt.rm(self.cwd)
        logger.info("Succesfully removed: " + self.cwd)
      else:
        logger.info("Abort jt.rm")
      return
    # Remove jobs from jid ( is this possible natively? )
    ## Use this if needed: jobtree._impl._JobTree__select_dir('.')[3040]
    for jid in list_jid:
      ## Try to check that each jid is valid integer.
      try:
        jid = int(jid)  
      except:
        logger.error('Failed to parse jid: %r'%jid)
      rmarg = self.cwd + '/' + str(jid)
      logger.debug("Removing rmarg: %r"%rmarg)
      ## Try the public API
      try:
        jt.rm(rmarg)
      except Exception, e:
        logger.warning(e)
        ## Try remove with internal API
        del jt._impl._JobTree__select_dir(self.cwd)[jid]
      logger.info("Removed: %r"%rmarg)

  @reset_cwd_after
  @forbid_root  
  def close(self):
    """By marking it close, it'll show only partial info"""
    logger.info('Closing: '+self.cwd)
    name = self.cwd.split('/')[-1]
    if not name.endswith(TAG_CLOSE):
      self.rename(name+TAG_CLOSE)

  @reset_cwd_after
  @forbid_root
  def open(self):
    """Opposite of close()"""
    logger.info('Opening: '+self.cwd)
    name = self.cwd.split('/')[-1]
    if name.endswith(TAG_CLOSE):
      self.rename(name[0:-len(TAG_CLOSE)])

  @reset_cwd_after
  def clean(self):
    """
    Explicitly remove all missing jobs recursively in this tree, start from root.
    """
    list_bad_jid = sorted([ jid for jid in self.jobs if not self.job(jid) ])
    print '\nList of jobs pending for cleaning::'
    print list_bad_jid
    if 'Y' != str(raw_input('Proceed with cleaning? Y/[n]: ')):
      print 'Abort cleaning'
      return
    for jid in list_bad_jid:
      paths = jt.find(jid) + jt.find(str(jid)) # Some version mixup jid type
      for path in paths:
        rmarg = path + '/' + str(jid)
        jt.rm(rmarg)
        logger.info("Removed: %r"%rmarg)

  @reset_cwd_after
  def help(self):
    """
    Show the help message
    """
    print "\x1b[2J"   # clear line
    print doc
    print '\n'
