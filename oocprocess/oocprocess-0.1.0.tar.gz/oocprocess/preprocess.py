"""
Preprocessing for big data analysis

@author: Alan Xu
"""

import os
import subprocess
import numpy as np
import pandas as pd
import zarr
from osgeo import gdal
import h5py
import dask.array as da
import dask.dataframe as dd
from dask import delayed
import xarray as xr


@delayed
def hdf5_load_tif(in_file, out_file, chunk_size=3000):
    in0 = gdal.Open(in_file)
    in0_shape = (in0.RasterCount, in0.RasterYSize, in0.RasterXSize)
    print('Input file ({}) \n dimension: {}'.format(os.path.basename(in_file), in0_shape))
    with h5py.File(out_file, 'w') as f:
        data_set = f.create_dataset('/ds', shape=in0_shape, chunks=(1, chunk_size, chunk_size))
        for i in range(0, in0.RasterXSize, chunk_size):
            for j in range(0, in0.RasterYSize, chunk_size):
                for k in range(in0.RasterCount):
                    band = in0.GetRasterBand(k + 1)
                    data = band.ReadAsArray(i, j, min(chunk_size, in0.RasterXSize - i),
                                            min(chunk_size, in0.RasterYSize - j))
                    data_set[k, j:j + min(chunk_size, in0.RasterYSize - j),
                    i:i + min(chunk_size, in0.RasterXSize - i)] = data
        print(data_set.shape)
        x = da.from_array(data_set, chunks=(1, chunk_size, chunk_size))
    return x


# @delayed
def zarr_load_tif(in_file, out_file, chunk_size=5000):
    in0 = gdal.Open(in_file)
    in0_shape = (in0.RasterCount, in0.RasterYSize, in0.RasterXSize)
    print('Input file ({}) \n dimension: {}'.format(os.path.basename(in_file), in0_shape))
    data_set = zarr.open_array('{}.zarr'.format(out_file), shape=in0_shape,
                               chunks=(1, chunk_size, chunk_size),
                               synchronizer=zarr.ThreadSynchronizer())
    for i in range(0, in0.RasterXSize, chunk_size):
        for j in range(0, in0.RasterYSize, chunk_size):
            for k in range(in0.RasterCount):
                band = in0.GetRasterBand(k + 1)
                data = band.ReadAsArray(i, j, min(chunk_size, in0.RasterXSize - i),
                                        min(chunk_size, in0.RasterYSize - j))
                data_set[k, j:j + min(chunk_size, in0.RasterYSize - j),
                i:i + min(chunk_size, in0.RasterXSize - i)] = data
    print(data_set)
    x = da.from_array(data_set, chunks=(1, chunk_size, chunk_size))
    return x


@delayed
def array_reshape(loaded_list, da_y, name='tmp', valid_min=0, chunk_size=5000000):
    loaded_list.append(da_y)
    da_data = da.concatenate(loaded_list, axis=0)
    ncol = da_data.shape[0]
    da_flat = da_data.reshape((ncol, -1)).T
    file_id = zarr.open_array('{}_id.zarr'.format(name), shape=(da_flat.shape[0],),
                              chunks=chunk_size, synchronizer=zarr.ThreadSynchronizer())
    da.store(da.arange(da_flat.shape[0], chunks=chunk_size), file_id)
    da_id = da.from_array(file_id, chunks=(chunk_size,))
    da_out = da.concatenate([da_id[:, None], da_flat], axis=1)
    col_names = ['id'] + ['x{}'.format(i) for i in range(ncol - 1)] + ['y']
    df = dd.from_dask_array(da_out, columns=col_names)
    df_valid = df[df.y > valid_min]
    df_valid = df_valid.set_index('id')
    num = int(np.ceil(df_valid.size / chunk_size))
    print('Number of partitions: {}'.format(num))
    df_valid = df_valid.repartition(npartitions=num)
    df_valid.to_csv('{}_*.csv'.format(name))
    return df_valid


# @delayed
def array_reshape_mxn(loaded_list, da_y, name='tmp', m=1, n=1, valid_min=0, chunk_size=250000):
    da_chunk = 5000
    da_data0 = da.concatenate(loaded_list, axis=0)
    dim0 = da_data0.shape
    zarr0 = zarr.open_array('{}_x0.zarr'.format(name), shape=dim0, chunks=(1, da_chunk, da_chunk),
                            synchronizer=zarr.ThreadSynchronizer())
    da.store(da_data0, zarr0)
    da_data0 = da.from_array(zarr0, chunks=(1, da_chunk, da_chunk))
    drow, dcol = np.mgrid[-m:m + .1, -n:n + .1].astype('int64')
    data_list = [da_y]
    for k in range(drow.size):
        zarr1 = zarr.open_array('{}_{}.zarr'.format(name, k), shape=dim0, chunks=(1, da_chunk, da_chunk),
                                synchronizer=zarr.ThreadSynchronizer())
        print(zarr1)
        # da.store(da_data0, zarr1)
        # da_data1 = da.from_array(zarr0, chunks=(1, da_chunk, da_chunk))
        # da_data1 = da.roll(da.roll(da_data1, drow.ravel()[k], axis=1), dcol.ravel()[k], axis=2)
        tmp1 = da.roll(da.roll(da_data0, drow.ravel()[k], axis=1), dcol.ravel()[k], axis=2)
        da.store(tmp1, zarr1)
        da_data1 = da.from_array(zarr1, chunks=(1, da_chunk, da_chunk))
        data_list.append(da_data1)

    da_data = da.concatenate(data_list, axis=0)
    ncol1 = drow.size
    ncol = da_data.shape[0]
    # da_data = da_data.reshape((ncol, -1)).T
    # zarr2 = zarr.open_array('{}_data.zarr'.format(name), shape=(dim0[1]*dim0[2], ncol),
    #                         chunks=(chunk_size, ncol), synchronizer=zarr.ThreadSynchronizer())
    # da.store(da_data, zarr2)
    # da_flat = da.from_array(zarr2, chunks=(chunk_size, ncol))
    da_flat = da_data.reshape((ncol, -1)).T
    file_id = zarr.open_array('{}_id.zarr'.format(name), shape=(dim0[1] * dim0[2],),
                              chunks=chunk_size, synchronizer=zarr.ThreadSynchronizer())
    da.store(da.arange(dim0[1] * dim0[2], chunks=chunk_size), file_id)
    da_id = da.from_array(file_id, chunks=(chunk_size,))
    da_out = da.concatenate([da_id[:, None], da_flat], axis=1)
    col_names = ['id'] + ['y'] + ['x_{}_{}'.format(i, j) for i in range(ncol1) for j in range(dim0[0])]
    print(col_names)
    df = dd.from_dask_array(da_out, columns=col_names)

    df.to_csv('{}_df0_*.csv'.format(name))
    df = dd.read_csv('{}_df0_*.csv'.format(name))
    # dd.to_parquet(df, '{}_df0_parq'.format(name), compression='snappy')
    # df = dd.read_parquet('{}_df0_parq'.format(name))

    df_valid = df[df.y > valid_min]
    df_valid = df_valid.set_index('id')
    num = int(np.ceil(df_valid.size / chunk_size))
    print('Number of partitions: {}'.format(num))
    df_valid = df_valid.repartition(npartitions=num)
    df_valid.to_csv('{}_*.csv'.format(name))

    return df_valid


@delayed
def array_reshape_rolling(x_files, y_file, name='tmp', m=1, n=1, valid_min=0, chunk_size=5000):
    x0 = []
    for x_file0 in x_files:
        x_name0 = os.path.splitext(os.path.basename(x_file0))[0]
        rio = xr.open_rasterio(x_file0, chunks={'band': 1, 'y': chunk_size, 'x': chunk_size})
        x0.append(rio)
    x_array = xr.concat(x0, dim='band')
    x_array['band'] = np.arange(x_array.shape[0])
    y_array = xr.open_rasterio(y_file, chunks={'band': 1, 'y': chunk_size, 'x': chunk_size})
    y_array = y_array.squeeze('band').drop('band')
    x_array.to_netcdf('{}_x0.nc'.format(name))
    y_array.to_netcdf('{}_y0.nc'.format(name))
    x_array = xr.open_dataarray('{}_x0.nc'.format(name), chunks={'band': 1, 'y': chunk_size, 'x': chunk_size})
    y_array = xr.open_dataarray('{}_y0.nc'.format(name), chunks={'y': chunk_size, 'x': chunk_size})

    drow, dcol = np.mgrid[-m:m + .1, -n:n + .1].astype('int64')
    y1 = y_array.expand_dims('band')
    y1['band'] = np.array([1])
    x1 = [y1]
    y1a = [y1]
    for k in range(drow.size):
        print([drow.flatten()[k], dcol.flatten()[k]])
        roll0 = x_array.roll(y=drow.flatten()[k]).roll(x=dcol.flatten()[k]).drop(['y', 'x'])
        roll0.to_netcdf('{}_x1_{}.nc'.format(name, k))
        roll0 = xr.open_dataarray('{}_x1_{}.nc'.format(name, k), chunks={'band': 1, 'y': chunk_size, 'x': chunk_size})
        x1.append(roll0)
        roll0 = y1.roll(y=drow.flatten()[k]).roll(x=dcol.flatten()[k]).drop(['y', 'x'])
        roll0.to_netcdf('{}_y1_{}.nc'.format(name, k))
        roll0 = xr.open_dataarray('{}_y1_{}.nc'.format(name, k), chunks={'band': 1, 'y': chunk_size, 'x': chunk_size})
        y1a.append(roll0)
    x1_array = xr.concat(x1, 'band')
    x1_array['band'] = ['target', ] + ['x_b{}_r{}'.format(i, j)
                                       for j in np.arange(drow.size) for i in np.arange(x_array.shape[0])]
    y1_array = xr.concat(y1a, 'band')
    y1_array['band'] = ['target', ] + ['y_b{}_r{}'.format(i, j)
                                       for j in np.arange(drow.size) for i in np.arange(y1.shape[0])]
    x1_new = x1_array.where(y_array > valid_min)
    x_out = x1_new.stack(sample=('y', 'x')).T
    y1_new = y1_array.where(y_array > valid_min)
    y_out = y1_new.stack(sample=('y', 'x')).T
    # x_shape = x_out.shape
    # x_out.to_netcdf('{}_x_out.nc'.format(name))
    # x_out = xr.open_dataarray('{}_x_out.nc'.format(name), chunks=(chunk_size, x_shape[1]))

    x_valid = x_out.dropna('sample', how='all')
    y_valid = y_out.dropna('sample', how='all')
    # x_valid = x_out.dropna('sample', how='all').reset_index('sample')
    # y_valid = y_out.dropna('sample', how='all').reset_index('sample')
    # x_valid.to_netcdf('{}_x_valid.nc'.format(name))
    # y_valid.to_netcdf('{}_y_valid.nc'.format(name))
    # x_valid = xr.open_dataarray('{}_x_valid.nc'.format(name),
    #                             chunks={'sample': chunk_size*100, 'band': x_valid.shape[1]})
    # y_valid = xr.open_dataarray('{}_y_valid.nc'.format(name),
    #                             chunks={'sample': chunk_size*100, 'band': y_valid.shape[1]})
    # x_valid = x_valid.set_index(sample=('y', 'x'))
    # y_valid.set_index(sample=('y', 'x')).to_pandas().to_csv('{}_y_valid.csv'.format(name))
    df = x_valid.to_pandas()
    df.to_csv('{}_x_valid.csv'.format(name))
    y_valid.to_pandas().to_csv('{}_y_valid.csv'.format(name))

    return df


def df_to_geotiff(df, ref_file, chunk_size=5000, name='out_array'):
    in0 = gdal.Open(ref_file, gdal.GA_ReadOnly)
    in_data = xr.open_rasterio(ref_file, chunks={'band': 1, 'y': chunk_size, 'x': chunk_size})
    in_data = in_data.squeeze('band').drop('band')
    mask = xr.zeros_like(in_data)
    y2 = xr.DataArray(df)

    y_out = y3.combine_first(mask)

    ndim = (in0.RasterYSize, in0.RasterXSize)
    print(ndim)
    flat_shape = int(ndim[0] * ndim[1])
    data_index = list(range(0, flat_shape, chunk_size))
    data_index.append(flat_shape)
    data_set = zarr.open_array('{}.zarr'.format(name), shape=(flat_shape,),
                               chunks=chunk_size, synchronizer=zarr.ThreadSynchronizer())
    for i in range(len(data_index) - 1):
        y_df = y_data.loc[data_index[i]:data_index[i + 1] - 1]
        data_set = update_da_values(data_set, y_df, data_index[i], data_index[i + 1])
    print(data_set)
    array_out = da.from_array(data_set, chunks=(chunk_size,))
    array_out = da.rechunk(array_out.reshape(ndim), (512, 512))

    driver = gdal.GetDriverByName('GTiff')
    ds = driver.CreateCopy('{}.tif'.format(name), in0, 0, ['COMPRESS=LZW', 'PREDICTOR=2', 'BIGTIFF=YES'])
    ds.GetRasterBand(1).WriteArray(np.array(array_out))
    ds = None
    return array_out


# @delayed
# def update_dd_values(y_data, data_set, chunks=None, block_id=None):
#     id0 = np.array(y_data.index)
#     z0 = np.full(np.ptp(id0)+1, np.nan)
#     z0[id0-min(id0)] = y_data.y
#     data_set[min(id0):max(id0)+1] = z0
#     return data_set


# @delayed
# def y_to_array(y_data, array_mask, valid_min=0, chunk_size=5000000, name='out_array'):
#     ndim = array_mask.shape
#     array_flat = array_mask.reshape(-1)
#     array_flat = da.rechunk(array_flat, chunks=(chunk_size,))
#     data_set = zarr.open_array('{}.zarr'.format(name), shape=array_flat.shape,
#                               chunks=chunk_size, synchronizer=zarr.ThreadSynchronizer())
#     # array_out = da.map_blocks(update_da_values, array_flat, y_data)
#     data_set = dd.map_partitions(update_dd_values, y_data, data_set)
#     array_out = da.from_array(data_set, chunks=(chunk_size,))
#     array_out = array_out.reshape(ndim)
#     da.to_hdf5('{}.h5'.format(name), '/y', array_out)
#     return array_out


# @delayed
def update_da_values(da_data, y_data, i0, i1):
    print(i1)
    print(type(i1))
    z0 = np.full((i1 - i0,), np.nan)
    # z0[y_data.loc[i0:i1-1].index.astype('uint64')] = y_data.loc[i0:i1-1].y
    z0[y_data.index.astype(int) - i0] = y_data.y
    z0[z0 < 0] = 0
    da_data[i0:i1] = z0
    return da_data


# @delayed
# def y_to_da(y_data, array_mask, valid_min=0, chunk_size=5000000, name='out_array'):
#     ndim = np.squeeze(array_mask).shape
#     print(ndim)
#     flat_shape = int(ndim[0]*ndim[1])
#     data_index = list(range(0, flat_shape, chunk_size))
#     data_index.append(flat_shape)
#     data_set = zarr.open_array('{}.zarr'.format(name), shape=(flat_shape,),
#                               chunks=chunk_size, synchronizer=zarr.ThreadSynchronizer())
#     for i in range(len(data_index) - 1):
#         y_df = y_data.loc[data_index[i]:data_index[i+1]-1]
#         update_da_values(data_set, y_df, data_index[i], data_index[i+1])
#     array_out = da.from_array(data_set, chunks=(chunk_size,))
#     array_out = array_out.reshape(ndim)
#     # da.to_hdf5('{}.h5'.format(name), '/y', array_out)
#     return array_out


# @delayed
def y_to_geotiff(y_data, ref_file, chunk_size=5000000, name='out_array'):
    in0 = gdal.Open(ref_file, gdal.GA_ReadOnly)
    ndim = (in0.RasterYSize, in0.RasterXSize)
    print(ndim)
    flat_shape = int(ndim[0] * ndim[1])
    data_index = list(range(0, flat_shape, chunk_size))
    data_index.append(flat_shape)
    data_set = zarr.open_array('{}.zarr'.format(name), shape=(flat_shape,),
                               chunks=chunk_size, synchronizer=zarr.ThreadSynchronizer())
    for i in range(len(data_index) - 1):
        y_df = y_data.loc[data_index[i]:data_index[i + 1] - 1]
        data_set = update_da_values(data_set, y_df, data_index[i], data_index[i + 1])
    print(data_set)
    array_out = da.from_array(data_set, chunks=(chunk_size,))
    array_out = da.rechunk(array_out.reshape(ndim), (512, 512))

    driver = gdal.GetDriverByName('GTiff')
    ds = driver.CreateCopy('{}.tif'.format(name), in0, 0, ['COMPRESS=LZW', 'PREDICTOR=2', 'BIGTIFF=YES'])
    ds.GetRasterBand(1).WriteArray(np.array(array_out))
    ds = None
    return array_out
