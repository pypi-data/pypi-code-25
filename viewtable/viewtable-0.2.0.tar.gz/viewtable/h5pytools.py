from contextlib import contextmanager
import glob
import os
import sys
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import h5py
import numpy as np
import pandas as pd



@contextmanager
def h5py_open(fname, mode='w'):
    """Context manager for opening hdf5 files and closing on exit."""
    f = h5py.File(fname)
    yield f
    f.close()


def quick_dump(fname, dictionary):
    """Given a dictionary, make hdf5 file containing datasets named by keys with data=values"""
    with h5py_open(fname, 'w') as f:
        f.attrs['original_file_name'] = fname
        f.attrs['HDF5_version'] = h5py.version.hdf5_version
        f.attrs['h5py_version'] = h5py.version.version
        for k, v in dictionary.items():
            f.create_dataset(k, data=v)


class h5Array:
    """Array wrapper class for using hdf5 / pandas.

    Basically to avoid trying to print anything during df viewing. Indexing
    semantics are simply passed on to the underlying h5py dataset, so this behaves
    just like that datatype (ie to get the entire dataset as a np array just
    do  data = h5Array[:] )
    """

    def __init__(self, dataset):
        self._dataset = dataset
        self.shape = dataset.shape
        self.dtype = dataset.dtype
        self.attrs = dict(self._dataset.attrs.items())

    def __getitem__(self, idx):
        return self._dataset[idx]

    def __str__(self):
        if len(self.shape) == 1:
            shape = '({})'.format(self.shape[0])
        else:
            shape = str(self.shape)
        return 'h5Array<{}>{}'.format(self.dtype, shape)

    def __repr__(self):
        return str(self)


def dict_from_file(file, with_metadata=True):
    """Transform simple hdf5 file with only one layer (/root/datasets) of primitives / nparrays into dictionary"""
    f = h5py.File(file, 'r')
    meta = dict(f.attrs)
    scalars = {k: v[()] for k, v in f.items() if v.shape == ()}
    arrays = {k: h5Array(v) for k, v in f.items() if v.shape != ()}
    if with_metadata:
        result = {**meta, **scalars, **arrays}
    else:
        result = {**scalars, **arrays}
    return result


def DataFrame_from_hdf5(files, sort_columns=True, *args, **kwargs):
    """Make dataframe from hdf5 files with the same restrictions as dict_from_file

    args and kwargs are passed to dict_from_file
    """
    try:
        files = [] + files
    except TypeError:
        files = [files]
    if not files:
        warnings.warn('No files were given to DataFrame_from_hdf5')
        return None
    dicts = []
    for file in files:
        try:
            d = dict_from_file(file, *args, **kwargs)
            dicts.append({**d, **{'filename': file}})
        except OSError:
            raise FileNotFoundError(file) from None

    df = pd.DataFrame(dicts).set_index('filename')
    if sort_columns:
        cols_lengths = {cols: len(str(vals)) for cols, vals in zip(df.columns.tolist(), df.iloc[0])}
        sorted_cols = sorted(cols_lengths, key=lambda k: cols_lengths[k])
        df = df[sorted_cols]
    return df
