"""
The SNIPES module, used for running simulations with the cosmological
simulation code SWIFT.

Maintained by Josh Borrow & Bert Vandenbroucke.

Licensed with GPLv2.
"""

import logging
import sys

name = "snipes"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)

logger.addHandler(ch)
