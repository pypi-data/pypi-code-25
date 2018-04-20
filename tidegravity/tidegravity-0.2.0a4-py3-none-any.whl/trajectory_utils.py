# -*- coding: utf-8 -*-

from datetime import datetime
import pandas as pd
import numpy as np


def convert_gps_time(gpsweek, gpsweekseconds, format='unix'):
    """
    Converts a GPS time format (weeks + seconds since 6 Jan 1980) to a UNIX
    timestamp (seconds since 1 Jan 1970) without correcting for UTC leap
    seconds.

    Static values gps_delta and gpsweek_cf are defined by the below functions
    (optimization) gps_delta is the time difference (in seconds) between UNIX
    time and GPS time.

    gps_delta = (dt.datetime(1980, 1, 6) - dt.datetime(1970, 1, 1)).total_seconds()

    gpsweek_cf is the coefficient to convert weeks to seconds
    gpsweek_cf = 7 * 24 * 60 * 60  # 604800

    Parameters
    ----------
    gpsweek : int, Series
        Number of weeks since beginning of GPS time (1980-01-06 00:00:00)

    gpsweekseconds : float, Series
        Number of seconds since the GPS week parameter

    format : {'unix', 'datetime'}
        Format of returned value

    Returns
    -------
    float or :obj:`datetime`
        UNIX timestamp (number of seconds since 1970-01-01 00:00:00) without
        leapseconds subtracted if 'unix' is specified for format.
        Otherwise, a :obj:`datetime` is returned.
    """
    # GPS time begins 1980 Jan 6 00:00, UNIX time begins 1970 Jan 1 00:00
    gps_delta = 315964800.0
    gpsweek_cf = 604800

    if isinstance(gpsweek, pd.Series) and isinstance(gpsweekseconds, pd.Series):
        gps_ticks = (gpsweek.astype('float64') * gpsweek_cf) + gpsweekseconds.astype('float64')
    else:
        gps_ticks = (float(gpsweek) * gpsweek_cf) + float(gpsweekseconds)

    timestamp = gps_delta + gps_ticks

    if format == 'unix':
        return timestamp
    elif format == 'datetime':
        return datetime(1970, 1, 1) + pd.to_timedelta(timestamp, unit='s')


def interp_nans(y):
    nans = np.isnan(y)
    x = lambda z: z.nonzero()[0]
    y[nans] = np.interp(x(nans), x(~nans), y[~nans])
    return y


def import_trajectory(filepath, delim_whitespace=False, interval=0,
                      interp=False, columns=None, skiprows=None, timeformat='hms'):
    """
    Read and parse ASCII trajectory data in a comma-delimited format.

    Parameters
    ----------
    filepath : str or File-like object.
        Filesystem path to trajectory data file
    delim_whitespace : bool
    interval : float, Optional
        Output data rate. Default behavior is to infer the rate.
    interp : Union[List[str], List[int]], Optional
        Gaps in data will be filled with interpolated values. List of
        column indices (list of ints) or list of column names (list of strs)
        to interpolate. Default behavior is not to interpolate.
    is_utc : bool, Optional
        Indicates that the timestamps are UTC. The index datetimes will be
        shifted to remove the GPS-UTC leap second offset.
    columns : List[str]
        Strings to use as the column names.
        If none supplied (default), columns will be determined based on
        timeformat
    skiprows : Union[None, Iterable, int, Callable], Optional
        Line numbers to skip (0-indexed) or number of lines to skip (int) at
        the start of the file. If callable, the callable function will be
        evaluated against the row indices, returning True if the row should
        be skipped and False otherwise. An example of a valid callable argument
        would be lambda x: x in [0, 2].
    timeformat : str
        'sow' | 'hms' | 'serial'  Default: 'hms'
        Indicates the time format to expect. The 'sow' format requires a field
        named 'week' with the GPS week, and a field named 'sow' with the GPS
        seconds of week. The 'hms' format requires a field named 'mdy' with the
        date in the format 'MM/DD/YYYY', and a field named 'hms' with the time
        in the format 'HH:MM:SS.SSS'. The 'serial' format (not yet implemented)
        requires a field named 'datenum' with the serial date number.

    Returns
    -------
    DataFrame
        Pandas DataFrame of ingested Trajectory data.

    """

    df = pd.read_csv(filepath, delim_whitespace=delim_whitespace, header=None,
                     engine='c', na_filter=False, skiprows=skiprows)

    # assumed position of these required fields
    if columns is None:
        if timeformat.lower() == 'sow':
            columns = ['week', 'sow', 'lat', 'long', 'ell_ht']
        elif timeformat.lower() == 'hms':
            columns = ['mdy', 'hms', 'lat', 'long', 'ell_ht']
        elif timeformat.lower() == 'serial':
            columns = ['datenum', 'lat', 'long', 'ell_ht']
        else:
            raise ValueError('timeformat value {fmt!r} not recognized'
                             .format(fmt=timeformat))

    # 'None' indicates a not-needed field
    # if a field is after all non-essentials, and is not named, it will be removed
    if len(df.columns) > len(columns):
        columns.extend([None] * (len(df.columns) - len(columns)))

    # drop unwanted columns
    drop_list = list()
    for idx, val in enumerate(columns):
        if val is None:
            drop_list.append(idx)

    columns = [x for x in columns if x is not None]

    if drop_list:
        df.drop(df.columns[drop_list], axis=1, inplace=True)

    df.columns = columns

    # create index
    if timeformat == 'sow':
        df.index = convert_gps_time(df['week'], df['sow'], format='datetime')
        df.drop(['sow', 'week'], axis=1, inplace=True)
    elif timeformat == 'hms':
        df.index = pd.to_datetime(df['mdy'].str.strip() + df['hms'].str.strip(),
                                  format="%m/%d/%Y%H:%M:%S.%f")
        df.drop(['mdy', 'hms'], axis=1, inplace=True)
    elif timeformat == 'serial':
        raise NotImplementedError
        # df.index = datenum_to_datetime(df['datenum'])

    # remove leap second
    # if is_utc:
        # TODO: Check dates at start and end to determine whether a leap second was added in the middle of the survey.
        # shift = leap_seconds(df.index[0])
        # df.index = df.index.shift(-shift, freq='S')

    # set or infer the interval
    # TODO: Need to infer interval for both cases to know whether resample
    if interval > 0:
        offset_str = '{:d}U'.format(int(interval * 1e6))
    else:
        offset_str = '100000U'

    # fill gaps with NaNs
    new_index = pd.date_range(df.index[0], df.index[-1], freq=offset_str)
    df = df.reindex(new_index)

    if interp:
        numeric = df.select_dtypes(include=[np.number])
        numeric = numeric.apply(interp_nans)

        # replace columns
        for col in numeric.columns:
            df[col] = numeric[col]

    return df
