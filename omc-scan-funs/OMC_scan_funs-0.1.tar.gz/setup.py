from setuptools import setup, find_packages

setup(
    name='OMC_scan_funs',    # This is the name of your PyPI-package.
    version='0.1',                          # Update the version number for new releases
    description='A library of functions for parsing LIGO OMC scans',
    py_modules=['OMC_scan_funs_no_pandas_v2','peak_finder','real_time_scan'],                  # The name of your scipt, and also the command you'll be using for calling it
    author='Alexei Ciobanu',
    author_email='alexei.ciobanu95@gmail.com'
)
