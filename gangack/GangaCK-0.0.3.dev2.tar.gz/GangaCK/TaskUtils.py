
import os
import re
from glob import glob
from . import GPI, logger

__all__ = []


def valid( s, blacklist, whitelist ):
  ## If in blacklist, immediately reject.
  for pat in blacklist:
    if re.search( pat, s ):
      return False
  ## Check for whitelist only if it's non-null
  if not whitelist:
    return True
  for pat in whitelist:
    if re.search( pat, s ):
      return True
  ## Null-case
  return False


## PATCH based on v600r44
def LHCbTransform__createChainUnit(self, parent_units, use_copy_output=True):
  """
  FOR LHCbTransform class
  Create an output unit given this output data.

  Patch to allow MassStorageFile
  """
 
  logger.info('Using PATCHED method: createChainUnit')

  ## @e need a parent job that has completed to get the output files
  incl_pat_list = []
  excl_pat_list = []
  for parent in parent_units:
    if len(parent.active_job_ids) == 0 or parent.status != "completed":
      return None
    pid = parent._getParent().getID()
    for inds in self.inputdata:
      if inds._name == "TaskChainInput" and inds.input_trf_id == pid:
        incl_pat_list += inds.include_file_mask
        excl_pat_list += inds.exclude_file_mask
 
  ## go over the output files and copy the appropriates over as input files
  flist    = set()
  path_msf = GPI.config.Output.MassStorageFile['uploadOptions']['path']
  for parent in parent_units:
    job = GPI.jobs(parent.active_job_ids[0])
    ## If Task framework are just gonna force the splitting, 
    # then there's no need a support logic for non-splitting job.
    # job_list = job.subjobs if job.subjobs else [job]
    for sj in job.subjobs:
      for f in sj.outputfiles:
        ftype = f._impl._name
        if ftype is 'DiracFile':
          flist.add( 'LFN:' + f.lfn )
        ## Patch for LPHE-PANASAS. Based entirely on MassStorageFile
        elif ftype is 'MassStorageFile':
          # Do only namePattern for now.... 
          searchpath = os.path.join( path_msf, str(job.id), str(sj.id), f.namePattern )
          for fpath in glob(searchpath):
            flist.add( 'PFN:'+fpath )
        else:
          logger.warning('Unknown filetype, ignore: '+ftype)

  ## Apply filter once all collected
  logger.debug('Before filter: %s'%str(flist))
  flist = sorted([ uri for uri in flist if valid( uri, excl_pat_list, incl_pat_list )])
  logger.debug('After filter: %s'%str(flist))

  ## just do one unit that uses all data
  unit = GPI.LHCbUnit._impl()
  unit.name = "Unit %i" % len(self.units)
  unit.inputdata = GPI.LHCbDataset(flist)._impl
  return unit

#===============================================================================

## PATCH based on v600r44
def LHCbUnit__updateStatus(self, status):
  """
  Update status hook

  PATCH: Allow the deletion to continue even though the backend is not Dirac.
  """

  ## check for input data deletion of chain data
  if status == "completed" and self._getParent().delete_chain_input and len(self.req_units) > 0:

    # the inputdata field *must* be filled from the parent task
    # NOTE: When changing to inputfiles, will probably need to check for any specified in trf.inputfiles

    # check that the parent replicas have been copied by checking backend status == Done
    job_list = []
    for req_unit in self.req_units:
      trf = self._getParent()._getParent().transforms[ int( req_unit.split(":")[0] ) ]
      req_unit_id = req_unit.split(":")[1]
      if req_unit_id != "ALL":
        unit = trf.units[ int( req_unit_id ) ]
        job_list.append( GPI.jobs( unit.active_job_ids[0] ) )
      else:
        for unit in trf.units:
          job_list.append( GPI.jobs( unit.active_job_ids[0] ) )

    ## Checking backend
    ## PATCH: Check only in case of Dirac backend
    sj = None
    queue = (sj for j in job_list for sj in (j.subjobs if j.subjobs else [j]))
    for j in queue:
      if j.backend._impl._name is 'Dirac':
        if sj.backend.status is not "Done":
          return 

    ## Finally, do the removal
    job = GPI.jobs(self.active_job_ids[0])
    for f in job.inputdata.files:
      logger.warning("Removing chain inputdata file '%s'..." % f.name)
      f.remove()

  super(GPI.LHCbUnit._impl,self).updateStatus(status)
