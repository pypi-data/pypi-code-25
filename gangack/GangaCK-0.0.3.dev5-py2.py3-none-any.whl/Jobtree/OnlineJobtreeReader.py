
import re
from .. import GPI, JobUtils
from . import ROOTDIR
from .BaseJobtreeReader import BaseJobtreeReader

#===============================================================================

# def compose_size(intjid, status):
#   # Bypass if not final
#   if status not in ('completed', 'failed'):
#     return '      N/A'
#   else:
#     size_local  = JobUtils.job_pfn_size(intjid)
#     _,size_lfn  = JobUtils.job_lfn_size(intjid)
#     if size_local is None:
#       size_local = 0
#     if size_lfn is None:
#       size_lfn = 0
#     return '{:>9}'.format(JobUtils.humansize(size_local+size_lfn)) 

# def compose_time(intjid, status):
#   pass

#===============================================================================

class OnlineJobtreeReader(BaseJobtreeReader):
  """
  Simple, based on existing GPI, but slow.
  """

  def ls(self, cwd=ROOTDIR):
    return GPI.jobtree.ls(cwd)

  @property
  def jobs_all(self):
    return GPI.jobs.ids()

  def job(self, jid):
    return GPI.jobs(jid)

#===============================================================================

#  3185 | completed |    Z02TauTau 8TeV |   60 |     Bender |      LSF |                    Z02TauTau (1kevt/f) [0:60] CheckP2PV

class QuickOnlineJobtreeReader(BaseJobtreeReader):
  """
  Like above, but rely on GPI.jobs table instead which is much faster, 
  but can be error-prone (due to setting in .gangarc) 
  and having limited information.

  TODO: Should pro-actively check def with config.Display.jobs_columns
  """

  bint    = r'\s*(\d*)\s*'
  bstr    = r'\s*(.*?)\s*' 
  pattern = r'^'+r'\|'.join([bint, bstr, bstr, bint, bstr, bstr, bstr])+r'$'

  def ls(self, cwd=ROOTDIR):
    # In some case, discrepancy of int/str jid. Strange.
    res = GPI.jobtree.ls(cwd)
    res['jobs'] = [int(jid) for jid in res['jobs']]
    return res

  @property
  def jobs_all(self):
    return GPI.jobs.ids()

  def job(self, jid):
    if int(jid) not in self.jobs_all:
      return None
    job     = JobUtils.JobStruct()
    intjid  = int(jid)
    ## note, jobs.select works propertly only when using intjid
    raw = str(GPI.jobs.select(intjid,intjid)).split('\n')[-2]  # one line
    try:
      jid,status,name,lensj,app,backend,comment = re.findall(self.pattern, raw)[0] 
    except Exception, e:
      print 'JID', jid
      print 'RAW', raw
      raise e
    job.fqid    = jid 
    job.status  = status
    job.name    = name
    job.lensj   = lensj
    job.application = app
    job.application_char = JobUtils._application_char[ app ] # ERROR-Prone!
    job.backend = backend
    job.comment = comment
    return job

  # lensj     = list_raw[3].strip()
  # app       = list_raw[4].strip()
  # backend   = list_raw[5].strip()
  # # comment   = list_raw[-1].strip()
  # comment   = joffline.comment
  # # time      = None if status!='completed' else None # TODO: Provide timeelasep for complete one
  # time      = joffline.time
  # size      = None
  # size      = compose_size(intjid, status)
  # return locals()