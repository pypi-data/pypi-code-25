# -*- coding: utf-8 -*-

"""A PyBEL extension for handling BEL resources with Artifactory.

Installation
------------
Get the Latest
~~~~~~~~~~~~~~~
Download the most recent code from `GitHub <https://github.com/pybel/pybel-artifactory>`_ with:

.. code-block:: sh

   $ python3 -m pip install git+https://github.com/pybel/pybel-artifactory.git

For Developers
~~~~~~~~~~~~~~
Clone the repository from `GitHub <https://github.com/pybel/pybel-artifactory>`_ and install in editable mode with:

.. code-block:: sh

   $ git clone https://github.com/pybel/pybel-artifactory.git
   $ cd bio2bel
   $ python3 -m pip install -e .
"""

from . import deploy, hashing, history, latest, today
from .deploy import *
from .hashing import *
from .history import *
from .latest import *
from .today import *

__all__ = (
        deploy.__all__ +
        hashing.__all__ +
        history.__all__ +
        latest.__all__ +
        today.__all__
)

__version__ = '0.0.2'

__title__ = 'pybel_artifactory'
__description__ = 'A PyBEL extension for handling BEL resources with Artifactory'
__url__ = 'https://github.com/pybel/pybel-artifactory'

__author__ = 'Charles Tapley Hoyt'
__email__ = 'charles.hoyt@scai.fraunhofer.de'

__license__ = 'MIT License'
__copyright__ = 'Copyright (c) 2018 Charles Tapley Hoyt'
