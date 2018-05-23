# Copyright 2018 Robert Haas
# For license information, see LICENSE.TXT in the package root directory

from . import cluster_setup, univariate, multivariate

__all__ = [
    'cluster_setup',
    'univariate',
    'multivariate',
]

# Versioning scheme: Semantic Versioning
# - https://packaging.python.org/guides/distributing-packages-using-setuptools/#scheme-choices
# - https://semver.org
__version__ = '1.0.0'
