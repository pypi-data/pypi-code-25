
"""
Ganga decorators
"""

__all__ = (
  'ijob_handler',
)

import Utils
from . import GPI
from PythonCK.decorators import cache_to_file

class ijob_handler(cache_to_file):
  """
  Complete single decorator to use for my offline Job patches. 

  - Function decorated with this decorator will undergoes extra type-check
    for the first argument. Expecting an int/str/Job so that the intjid 
    can be extracted.
  - As a result, this can well be patched to Job class.
  - Because this deco is a subclass of `cache_to_file`, the rules for 
    `force_reload` and `early_giveup` follows
  - By construction, the writing-to-cache will only be enabled if the 
    status of job is final (i.e., completed / failed )

  """

  __slots__ = ()

  ## Redefine abstract method
  def _run(self, intjid, *args, **kwargs):

    ## Validate the required intjid first
    intjid = Utils.validate_intjid(intjid)
    if not intjid:
      raise ValueError('Expect first argument to be jid (int/str/Job)')

    ## Access to input_skip_write, depends on the current status
    # Late import to avoid circular-dependency

    is_final = GPI.jobs(intjid).is_final
    self._logd('is_final: %r'%is_final)
    # self._isw = (not is_final) # If ongoing, skip write.
    self._isw = lambda *args,**kwargs: not is_final

    # print intjid, is_final

    ## Finally, return super
    return super(ijob_handler,self)._run(intjid, *args, **kwargs)

#------------------------------------------------------------------------------
