
"""
Collection of helper methods to be unused inside Ganga6.

To bind with Ganga on start-up, add the following line to 
`~/.ipython-ganga/ipythonrc`

import_mod MyGanga

"""

__author__  = 'Chitsanu Khurewathanakul'
__email__   = 'chitsanu.khurewathanakul@epfl.ch'
__license__ = 'GNU GPLv3'

## 3rd-Party lib
from PythonCK import logger

## Flag
_HAS_GANGA = False
IS_GANGA61 = False

try:
  # Provide binders...
  from Ganga import GPI
  logger.reinit_blacklist() 
  logger.info("GangaCK imported successfully!")
  _HAS_GANGA  = True
  import re
  IS_GANGA61 = re.findall( r'GANGA_(v\d+)', str(GPI))[0]=='v601'
except Exception as e:
  logger.warning(e)
  logger.warning("Cannot import library GangaCK, using OfflineGPI")
  # import ConfigUtils  # Used by some GPI, need pre-GPI late-import protection.
  import OfflineGPI as GPI

## Finally, apply patching, as it still needs for both online/offline GPI.
import __patcher__
del __patcher__

# Ensure again log level after import
# logger.setLevel(logger.INFO)
