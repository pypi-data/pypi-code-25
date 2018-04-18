from __future__ import absolute_import, division, print_function

import re
import six
import pandas as pd
import numpy as np

__all__ = ['to_datetime']


# Compatibility functions for older pandas versions.
if tuple(map(int, pd.__version__.split('.')[:2])) < (0, 17):
    def _pd_to_datetime_coerce(arg):
        return pd.to_datetime(arg, coerce=True)

    def _pd_to_numeric_coerce(arg):
        if not isinstance(arg, pd.Series):
            arg = pd.Series(arg)
        return arg.convert_objects(
            convert_dates=False, convert_numeric=True,
            convert_timedeltas=False)
else:
    def _pd_to_datetime_coerce(arg):
        return pd.to_datetime(arg, errors='coerce')

    def _pd_to_numeric_coerce(arg):
        return pd.to_numeric(arg, errors='coerce')


def _split_arg(arg):
    """Split a comma-separated string into a list."""
    if isinstance(arg, six.string_types):
        arg = [it for it in re.split(r'[\s,]+', arg) if it]
    return arg


def _extract_series_name(ds):
    """Extract series name from record set."""
    m = re.match(r'^\s*([\w\.]+).*$', ds)
    return m.group(1) if m is not None else None


def to_datetime(tstr, force=False):
    """
    Parse JSOC time strings.

    In general, this is quite complicated, because of the many
    different (non-standard) time strings supported by the DRMS. For
    more (much more!) details on this matter, see
    `Rick Bogart's notes <http://jsoc.stanford.edu/doc/timerep.html>`__.

    The current implementation only tries to convert typical HMI time
    strings, with a format like "%Y.%m.%d_%H:%M:%S_TAI", to an ISO time
    string, that is then parsed by pandas. Note that "_TAI", aswell as
    other timezone indentifiers like "Z", will not be taken into
    account, so the result will be a naive timestamp without any
    associated timezone.

    If you know the time string format, it might be better calling
    pandas.to_datetime() directly. For handling TAI timestamps, e.g.
    converting between TAI and UTC, the astropy.time package can be
    used.

    Parameters
    ----------
    tstr : string or list/Series of strings
        DateTime strings.
    force : bool
        Set to True to omit the endswith('_TAI') check.

    Returns
    -------
    result : pandas.Series or pandas.Timestamp
        Pandas series or a single Timestamp object.
    """
    s = pd.Series(tstr).astype(str)
    if force or s.str.endswith('_TAI').any():
        s = s.str.replace('_TAI', '')
        s = s.str.replace('_', ' ')
        s = s.str.replace('.', '-', n=2)
    res = _pd_to_datetime_coerce(s)
    return res.iloc[0] if (len(res) == 1) and np.isscalar(tstr) else res
