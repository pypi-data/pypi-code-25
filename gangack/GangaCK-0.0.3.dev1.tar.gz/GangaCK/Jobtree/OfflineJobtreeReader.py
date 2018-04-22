
import os
import re
from .. import GPI, logger, ConfigUtils, Utils
from . import ROOTDIR
from .BaseJobtreeReader import BaseJobtreeReader
from PythonCK.decorators import lazy_property

#-------------------------------------------------------------------------------
# OFFLINE Reader
#-------------------------------------------------------------------------------

def read(path):
  """
  Shortcut method to read all data in given external file.
  """
  with open(path) as fin:
    return ''.join(fin.readlines())

class OfflineJobtreeReader(BaseJobtreeReader):
  """
  Derived class to read the local jobtree file outside ganga interactive session.
  """

  __slots__ = ('dat', '_lazy_jobs_all')

  def __init__(self, datpath=None):
    """
    Args:
      datpath (string): Path to jobtree file. If None, it'll try to locate the
                        appropriate location by itself ( guessing jobs.metadata )

    >>> OfflineJobtreeReader('tests/res/jobtree_test')
    <GangaCK.Jobtree.OfflineJobtreeReader.OfflineJobtreeReader object at ...>

    """
    super(OfflineJobtreeReader, self).__init__()
    if not datpath:
      datpath = os.path.join(ConfigUtils.dir_repository(), 'jobs.metadata/0xxx/0/data')
    self.dat = eval(re.findall(r'{.*}', read(datpath))[0])

  def ls(self, cwd=ROOTDIR):
    """

    >>> ojtr = OfflineJobtreeReader('tests/res/jobtree_test')

    >>> pprint(ojtr.ls())
    {'folders': ['002 Z+BJet Analysis[CLOSED]', '013_Tau_Identification'],
     'jobs': []}

    >>> pprint(ojtr.ls('013_Tau_Identification'))
    {'folders': ['00_samples', '02_ditau_passthrough_v2', '03_Stripping23'],
     'jobs': []}

    >>> ojtr.ls('BADDIR')
    Traceback (most recent call last):
    ...
    KeyError: 'Missing key: BADDIR'

    >>> pprint(ojtr.ls('013_Tau_Identification/00_samples'))
    {'folders': [], 'jobs': [2543, 2811, 2812, 2861, 2862]}

    ## Ignore [CLOSED]

    >>> pprint(ojtr.ls('013_Tau_Identification/00_samples [CLOSED]'))
    {'folders': [], 'jobs': [2543, 2811, 2812, 2861, 2862]}

    >>> pprint(ojtr.ls('013_Tau_Identification[CLOSED]/00_samples'))
    {'folders': [], 'jobs': [2543, 2811, 2812, 2861, 2862]}

    >>> ojtr.jobs
    [197, 202, 232, 269, 892, 893, 894, 907, 2543, 2767, 2768, 2769, 2770, 2771, 2811, 2812, 2861, 2862]

    """
    d2 = dict(self.dat[ROOTDIR]) # Make a copy
    for s in cwd.split('/'):
      if s and (s != ROOTDIR):
        d2 = Utils.dictget_ignore_closed(d2, s)
    list_jobs = []
    list_dirs = []
    for key,val in sorted(d2.iteritems()):
      if isinstance(val, dict):
        list_dirs.append(key)
      else:
        list_jobs.append(int(key))
    return {'folders':list_dirs, 'jobs':list_jobs}

  def job(self, jid):
    """

    >>> _ = getfixture('job197')
    >>> ojtr = OfflineJobtreeReader('tests/res/jobtree_test')
    >>> j = ojtr.job(197)
    >>> '[{0.id}] {0.name}'.format(j)
    '[197] Z02MuMuLine'

    """
    if int(jid) not in self.jobs_all:
      return None
    try:
      return GPI.jobs(jid)
    except IOError, e:
      logger.warning(e)
      return None  # Corrupt job

  @lazy_property
  def jobs_all(self):
    """
    Use the combination of dirnames in repo+work.
    """
    s1 = ConfigUtils.jids_repository()
    s2 = ConfigUtils.jids_workspace()
    return s1.union(s2)

    # searchpath = os.path.join(self.gdir, 'repository/khurewat/LocalXML/6.0/jobs/*/*')
    # return [ int(re.findall(r'.*/(\d+)', s)[0]) for s in sorted(glob(searchpath)) ]
