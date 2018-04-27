# -*- coding: utf-8 -*-

__author__ = 'Uwe Schmitt'
__email__ = 'uwe.schmitt@id.ethz.ch'
__version__ = '0.4.2'

from ruamel import yaml
import warnings
warnings.simplefilter('ignore', yaml.error.UnsafeLoaderWarning)
