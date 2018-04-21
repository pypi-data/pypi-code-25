"""
This file is generated using an accompanying org file.
Do not edit manually.
"""

import xarray as xr
import numpy as np
from typing import List, Union
from ledge.datatypes import Truth, Loss
from ledge.utils import get_lag
from functools import partial

Series = Union[Truth, Loss]

def _get_right_envelope(ds: xr.Dataset) -> xr.DataArray:
    """
    Get an envelope of non nan values from the right
    """

    array = ds.to_array()
    n_cols = array.shape[0]

    col_idx = n_cols - 1 - np.flip(np.isnan(array), axis=0).argmin(dim="variable")
    return array.isel(variable = col_idx).rename({ "variable": "lag" })


def _merge_lags(series_list: List[Series]) -> xr.Dataset:
    """
    Create a left joined dataset
    """

    # Merge based on the longest series
    longest_series = max(series_list, key=len)
    reindexed_list = [ser.reindex_like(longest_series, copy=False) for ser in series_list]
    return xr.merge([ser.rename(get_lag(ser)) for ser in reindexed_list], join="left")

def latest(series_list: List[Series], sort_fn=get_lag) -> Series:
    """
    Return series with largest lag. Prefer series without lag set.
    """

    dataset = _merge_lags(sorted(series_list, key=sort_fn))
    latest_series = _get_right_envelope(dataset)
    latest_series.attrs = series_list[0].attrs
    latest_series.attrs.pop("lag", None)
    return latest_series

earliest = partial(latest, sort_fn=lambda l: -get_lag(l))
earliest.__doc__ = "Return series with smallest lag."
