"""
.. versionadded:: 0.3.3

Module containing quick plots for models fitted in statsmodels
"""

import logging
from .utils import get_single_figure

LOG = logging.getLogger(__name__)


def plot_residuals_glm(model, ax=None):
    if ax is None:
        fig, ax = get_single_figure(figsize=(5, 3))

    
