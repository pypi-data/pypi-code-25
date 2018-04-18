# -*- encoding: utf-8 -*-
from sparkmlpipe.utils import dependencies
from sparkmlpipe.__version__ import __version__


__MANDATORY_PACKAGES__ = '''
numpy>=1.14.2
pandas>=0.22.0
pyspark>=2.3.0
PyYAML>=3.12
'''

dependencies.verify_packages(__MANDATORY_PACKAGES__)
