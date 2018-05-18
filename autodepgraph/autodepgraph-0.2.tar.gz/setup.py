import re
from setuptools import setup

def get_version(verbose=1):
    """ Extract version information from source code """

    try:
        with open('autodepgraph/version.py', 'r') as f:
            ln = f.readline()
            m = re.search('.* ''(.*)''', ln)
            version = (m.group(1)).strip('\'')
    except Exception as E:
        print(E)
        version = 'none'
    if verbose:
        print('get_version: %s' % version)
    return version

version = get_version()

setup(name='autodepgraph',
      version=version,
      description='automated tuning based on dependency graph',
      author='Adriaan Rol et al',
      author_email='adriaan.rol@gmail.com',
	  license="BSD",
	  keywords =['graph', 'calibration framework'],
      url='https://github.com/AdriaanRol/AutoDepGraph',
	  packages=['autodepgraph'],
      ext_package='autodepgraph',
      requires=["qcodes", "pytools", "numpy", "pytest", "matplotlib"],
	  classifiers=['Development Status :: 4 - Beta', 'Intended Audience :: Science/Research',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                   ]
      )
