# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import pytest
import pandas as pd


def convert_matlab_serial_time(time: float):
    days = datetime.fromordinal(int(time))
    frac = timedelta(days=time % 1) - timedelta(days=366)
    return days + frac


def load_sample_dataset(fpath: str):
    df = pd.read_csv(fpath, header=0, names=['lon', 'lat', 'ser_time', 'g0'])

    dt_index = df['ser_time'].apply(convert_matlab_serial_time)
    dt_index.name = 'time'
    df.index = dt_index
    df['alt'] = 0
    df = df.drop(['ser_time'], axis=1)  # Drop the original ser_time column now that new index is set

    return df


@pytest.fixture(scope="module")
def matlab_df():
    return load_sample_dataset('tests/matlab_synthetic.csv')
