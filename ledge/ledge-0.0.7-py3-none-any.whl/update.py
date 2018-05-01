"""
This file is generated using an accompanying org file.
Do not edit manually.
"""

import xarray as xr
import numpy as np
from typing import List
from ledge.datatypes import Loss, Weight
from ledge.utils import uniform_weights

def noop(losses: List[Loss], init_weights=None) -> Weight:
    """
    Do nothing.
    """

    models = [loss.attrs["model"] for loss in losses]
    if init_weights is None:
        return uniform_weights(models, ones=False)
    else:
        return init_weights

def pick(losses: List[Loss], index: int, init_weights=None) -> Weight:
    """
    Return 1 weight for model at index and 0 for others
    """

    models = [loss.attrs["model"] for loss in losses]
    return xr.DataArray([1 if i == index else 0 for i in range(len(losses))],
                        dims="model", coords={ "model": models })

def ftl(losses: List[Loss], k=1, lookback=None, init_weights=None) -> Weight:
    """
    Follow the leader update. Give full weight to the k models with least loss.
    lookback says how many steps to sum the losses for.
    """

    if lookback is None or lookback < 0:
        lookback = 0

    loss_sums = [np.sum(loss[-lookback:]) for loss in losses]
    best_indices = np.argsort(loss_sums)[:k]

    weight_vec = np.zeros(len(losses))
    weight_vec[best_indices] = 1 / k

    models = [loss.attrs["model"] for loss in losses]
    return xr.DataArray(weight_vec, dims="model", coords={ "model" : models })

def ftpl(losses: List[Loss]) -> Weight:
    """
    Follow the perturbed leader update.
    """

    raise NotImplementedError()

def fixed_share(losses: List[Loss], eta: float, alpha: float, init_weights=None) -> Weight:
    r"""
    Fixed share update.
    """

    models = [loss.attrs["model"] for loss in losses]
    M = len(models)
    T = len(losses[0])

    if init_weights is None:
        weights = uniform_weights(models, ones=False)
    else:
        weights = init_weights

    # Vectorize this
    for t in range(T):
        vs = weights * np.exp([-eta * loss[t] for loss in losses])
        weights = (alpha * np.sum(vs) / M) + (1 - alpha) * vs

    return weights

def variable_share(losses: List[Loss]) -> Weight:
    r"""
    Variable share update.
    """

    raise NotImplementedError()

def mw(losses: List[Loss], eta: float, init_weights=None) -> Weight:
    r"""
    Multiplicative weight update. :math:`w_i(t + 1) = w_i(t) (1 - \eta m_i(t))`
    """

    models = [loss.attrs["model"] for loss in losses]

    if init_weights is None:
        init_weights = uniform_weights(models)

    updates = [np.prod(1 - eta * loss) for loss in losses]

    return init_weights * updates

def hedge(losses: List[Loss], eta: float, init_weights=None) -> Weight:
    r"""
    Exponential weight update. :math:`w_i(t + 1) = w_i(t) e^{- \eta m_i(t)}`
    """

    models = [loss.attrs["model"] for loss in losses]

    if init_weights is None:
        init_weights = uniform_weights(models)

    updates = [np.exp(-eta * np.sum(loss)) for loss in losses]

    return init_weights * updates
