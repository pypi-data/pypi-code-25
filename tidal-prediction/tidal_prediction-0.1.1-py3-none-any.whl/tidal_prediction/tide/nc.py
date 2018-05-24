"""
Module containing NetCDF methods used for the tidal prediction.
"""
# Standard library imports
import logging

# External imports
import netCDF4
import numpy as np

"""
def read_bathymetry(filename):
    # Reads bathymetry file.
    dataset = netCDF4.Dataset(filename, 'r')
    print(dataset)
    pass
"""

def create_outfile(filename, outputs, lat, lon):
    """Initialize output file."""
    dataset = netCDF4.Dataset(filename, "w", format="NETCDF4_CLASSIC")
    dataset.set_auto_maskandscale(True)

    # Define dimensions
    dataset.createDimension('time', None)
    dataset.createDimension('lat', len(lat))
    dataset.createDimension('lon', len(lon))
    
    # Define dimensional variables
    nctm = dataset.createVariable('time', np.float64, ('time'))
    nclat = dataset.createVariable('lat', np.float32, ('lat'))
    nclon = dataset.createVariable('lon', np.float32, ('lon'))
    nclon[:] = lon
    nclat[:] = lat

    # Set attributes for dimensional variables
    nclat.setncattr('long_name', 'latitude')
    nclat.setncattr('units', 'degrees_north')
    nclon.setncattr('long_name', 'longitude')
    nclon.setncattr('units', 'degrees_east')

    fill_value = netCDF4.default_fillvals['i2']  # -32767

    # Define u and v current variables
    if 'u' in outputs:
        ncu = dataset.createVariable('u', 'i2', ('time', 'lat', 'lon'),
                                     fill_value=fill_value)
        ncu.setncattr('long_name', 'eastward current')
        ncu.setncattr('units', 'm/s')
        ncu.setncattr('add_offset', 0.0)
        ncu.setncattr('scale_factor', 0.001)

    if 'v' in outputs:
        ncv = dataset.createVariable('v', 'i2', ('time', 'lat', 'lon'),
                                     fill_value=fill_value)
        ncv.setncattr('long_name', 'northward current')
        ncv.setncattr('units', 'm/s')
        ncv.setncattr('add_offset', 0.0)
        ncv.setncattr('scale_factor', 0.001)

    # Define U and V transport variables
    if 'U' in outputs:
        ncu = dataset.createVariable('U', 'i2', ('time', 'lat', 'lon'),
                                     fill_value=fill_value)
        ncu.setncattr('long_name', 'Eastward volume transport')
        ncu.setncattr('units', 'm**2/s')
        ncu.setncattr('add_offset', 0.0)
        ncu.setncattr('scale_factor', 0.1)

    if 'V' in outputs:
        ncv = dataset.createVariable('V', 'i2', ('time', 'lat', 'lon'),
                                     fill_value=fill_value)
        ncv.setncattr('long_name', 'Northward volume transport')
        ncv.setncattr('units', 'm**2/s')
        ncv.setncattr('add_offset', 0.0)
        ncv.setncattr('scale_factor', 0.1)

    # Define elevation variable
    if 'z' in outputs:
        ncz = dataset.createVariable('z', 'i2', ('time', 'lat', 'lon'),
                                     fill_value=fill_value)
        ncz.setncattr('long_name', 'sea surface elevation')
        ncz.setncattr('units', 'm')
        ncz.setncattr('add_offset', 0.0)
        ncz.setncattr('scale_factor', 0.001)

    # Define depth
    add_offset = 5000.0
    scale_factor = 0.25 # Values are from 0 to ~10000
    ncdepth = dataset.createVariable('depth', 'i2', ('lat', 'lon'),
                                     fill_value=fill_value)
    ncdepth.setncattr('long_name', 'sea floor level')
    ncdepth.setncattr('units', 'm')
    ncdepth.setncattr('add_offset', add_offset)
    ncdepth.setncattr('scale_factor',scale_factor)

    return dataset
