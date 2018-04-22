
# """
# Collection of commands exposed to interactive level. 

# It's preferable to do in magic's style instead if possible.
# """

# from . import *

# __all__ = (
#   'resubmit_incomplete',
# )


# def resubmit_incomplete(id, force_all=False, banning=False):
#   """
#   Helper method to correct the subjobs from given jobs id.
  
#     * SUBMITTING  ==> call force_status('failed')
#     * SUBMITTED   ==> call force_status('failed')
#     * KILLED      ==> Call force_status('failed')
#     * COMPLETING  ==> call .backend.reset()
#     * FAILED      ==> call resubmit()
#     * NEW         ==> call submit()

#   By default, this will have effect only on FAILED subjobs.
#   If force_all, it will apply all sequence above.

#   Args:
#     id (int): Id of given job 
#     force_all (bool, optional) : If False, the above procedures wlll only apply 
#                                 to the failed jobs. If True, apply all above.
#                                 (Default; False)
#     banning (bool, optiona) : If True, the previously used SE will be banned. 
#                               (Default; False)
#   """
#   if force_all:
#     raise NotImplementedError('See banning flag')
#     jobs(id).subjobs.select(status='submitting').force_status('failed')
#     jobs(id).subjobs.select(status='submitted').force_status('failed')
#     jobs(id).subjobs.select(status='killed').force_status('failed')
#     for sj in jobs(id).subjobs.select(status='completing'):
#       sj.backend.reset()
#     jobs(id).subjobs.select(status='new').submit()
#   # Apply BannedSites if requested (non-cumulative, just last one used.)
#   if banning and isinstance(jobs(id).backend, Dirac):
#     for sj in jobs(id).subjobs.select(status='failed'):
#       sj.backend.settings['BannedSites'] = [sj.backend.actualCE]
#   jobs(id).subjobs.select(status='failed').resubmit()

  
# #====================================================================

