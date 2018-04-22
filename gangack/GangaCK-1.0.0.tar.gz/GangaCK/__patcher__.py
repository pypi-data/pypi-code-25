
from . import GPI, logger

import JobUtils

try:
  ### Job
  GPI.Job.attach_mylib  = JobUtils.job_attach_mylib
  GPI.Job.ppl_list      = JobUtils.job_ppl_list
  GPI.Job.pfn_size      = JobUtils.job_pfn_size
  GPI.Job.lfn_list      = JobUtils.job_lfn_list
  GPI.Job.lfn_size      = JobUtils.job_lfn_size
  GPI.Job.lfn_purge     = JobUtils.job_lfn_purge
  GPI.Job.eos_list      = JobUtils.job_eos_list
  GPI.Job.__format__    = JobUtils.__format__
  GPI.Job.__eq__        = JobUtils.__eq__
  # Properties
  GPI.Job.humansize         = JobUtils.humansize
  GPI.Job.is_final          = JobUtils.is_final
  GPI.Job.lensj             = JobUtils.lensj
  GPI.Job.application_char  = JobUtils.application_char

  ### JobTemplate
  GPI.JobTemplate.attach_mylib = JobUtils.job_attach_mylib

  ### LHCbDataset
  import IOUtils
  GPI.LHCbDataset.new         = classmethod(IOUtils.LHCbDataset_new)
  GPI.LHCbDataset.__getitem__ = IOUtils.LHCbDataset__getitem__
  # GPI.LHCbDataset.__iadd__    = IOUtils.LHCbDataset__iadd__

  ## LHCbTransform
  # import TaskUtils
  # GPI.LHCbTransform._impl.createChainUnit = TaskUtils.LHCbTransform__createChainUnit
  # GPI.LHCbUnit._impl.updateStatus         = TaskUtils.LHCbUnit__updateStatus

  ## Applications
  import AppUtils
  GPI.Gauss.nickname    = staticmethod(AppUtils.Gauss__nickname)
  GPI.Gauss.optsfile    = AppUtils.app_optsfile    # Use python descriptor protocol instead of Ganga's
  GPI.Boole.optsfile    = AppUtils.app_optsfile    
  GPI.Moore.optsfile    = AppUtils.app_optsfile    
  GPI.Brunel.optsfile   = AppUtils.app_optsfile    
  GPI.DaVinci.optsfile  = AppUtils.app_optsfile    
  #
  # GPI.DaVinci.events    = AppUtils.DaVinci__events  ##
  # GPI.DaVinci._impl.events    = AppUtils.DaVinci__events  ##

  logger.info('Patching1 completed!')

except Exception, e:
  logger.warning('Patching1 failed.')
  logger.warning(e)

#--------------------------------------------------------#
# Part 2: MAGICS ( depends on version of IPython shell ) #
#--------------------------------------------------------#

try:

  # from IPython import get_ipython
  # print get_ipython()
#   from IPython.iplib import InteractiveShell as IS
  # from IPython.terminal.embed import InteractiveShellEmbed
  
  import Magics
  del Magics
  logger.info('Patching Magics completed!')
except Exception, e:
  logger.warning('Patching Magics failed.')
  logger.warning(e)
  
#   ### Magics

#   import Magics
#   IS.magic_peek   = Magics.magic_peek
#   IS.magic_jv     = Magics.magic_jv
#   IS.magic_jrm    = Magics.magic_jrm
#   IS.magic_jt     = Magics.magic_jt
#   IS.magic_grun   = Magics.magic_grun
#   IS.magic_resubmit   = Magics.magic_resubmit

#   import JobShell
#   IS.magic_jsh  = JobShell.magic_jsh


