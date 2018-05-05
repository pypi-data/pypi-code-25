"""
Setup oocprocess package.
"""

from setuptools import setup, find_packages

setup(
    name='oocprocess',
    version='0.1.0',
    description='Out-of-core Processing',
    url='https://gitlab.com/alanxuliang/a1704_oocprocess',

    author='Alan Xu',
    author_email='bireme@gmail.com',

    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: GIS',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='ooc data processing',
    # package_dir={'': 'src'},
    # packages=find_packages(where='src', exclude=['data', 'docs', 'tests']),
    packages=find_packages(exclude=['data', 'docs', 'tests']),

    install_requires=[
        'numpy',
        'pandas',
        'zarr',
        'dask',
        'h5py',
        'xarray',
        'GDAL>=2.0',
        'lxml',
        'scikit-learn>=0.18',
    ],

)
