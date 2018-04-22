"""

OffineGPI mimic limited functionalities in Ganga.GPI package,
providing practical interface for the rest of GangaCK in absense
of real `SetupGanga` environment.

- Compare to actual GPI, these provide attributes for *read* only.

"""

from .OfflineJob import OfflineJob as Job
from .config import Config

config  = Config()

#-----------#
# Functions #
#-----------#

def jobs(jid):
  """Support only getting job from single int for now..."""
  return Job(jid)

# dummy for now
jobtree = None

#--------------#
# Lite-classes #
#--------------#

BKQuery = type('BKQuery', (list,), {'getDataset': lambda x: LHCbDataset()})

DiracFile = type('DiracFile', (dict,), {
  'getMetadata': lambda x: dict(),
  'put'        : lambda x: None,
  'remove'     : lambda x: None,
})

JobTemplate = type('JobTemplate', (object,), {})

LocalFile = type('LocalFile', (object,), {})

LogicalFile = type('LogicalFile', (object,), {})

#---------#
# Classes #
#---------#

class File(object):
  def __init__( self, name ):
    self._name = name 
  @property 
  def name(self):
    return self._name

class LHCbDataset(object):

  def __init__(self, files=[], XMLCatalogueSlice=''):
    # super(LHCbDataset,self).__init__(files)
    self._files = [ File(x) for x in files ]
    self._XMLCatalogueSlice = File(XMLCatalogueSlice)

  @property
  def files(self):
    return self._files
  @property
  def XMLCatalogueSlice(self):
    return self._XMLCatalogueSlice

  def getCatalog(self):
    raise NotImplementedError  

#------------#
# SINGLETONS #
#------------#

_ThreadPoolQueueMonitor = type('ThreadPoolQueueMonitor', (), {
    'worker_status': [],
})

class _queues(object):
  @property  
  def _user_threadpool(self):
    return _ThreadPoolQueueMonitor()
  def add(self, func, args=(), kwargs={}, priority=5):
    pass

queues  = _queues()
