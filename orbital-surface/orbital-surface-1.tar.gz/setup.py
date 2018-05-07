'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Apr 4, 2018
@author: Niels Lubbes

https://python-packaging.readthedocs.io/en/latest/minimal.html
https://pypi.python.org/pypi?%3Aaction=list_classifiers
'''


from setuptools import setup


setup( 
    name = 'orbital-surface',
    version = '1',
    description = 'Python library for constructing and visualizing curves on surfaces',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Mathematics',
        ],
    keywords = 'curves surfaces parametrization Povray',
    url = 'http://github.com/niels-lubbes/orbital',
    author = 'Niels Lubbes',
    license = 'MIT',
    package_dir = {
        'orbital': 'src/orbital',
        'orbital.cossin': 'src/orbital/cossin',
        'orbital.pov': 'src/orbital/pov',
        'orbital.povray': 'src/orbital/povray',
        'orbital.prod': 'src/orbital/prod',
    },
    packages = ['orbital', 'orbital.cossin', 'orbital.pov', 'orbital.povray', 'orbital.prod'],
    # include_package_data = True,
    package_data = {'orbital': ['orb_tools.sobj'], 'orbital.cossin':['cos_sin.txt']},
    install_requires = ['linear_series'],
    test_suite = 'nose.collector',
    tests_require = ['nose'],
    entry_points = {
        'console_scripts': ['run-lattice=orbital.__main__:main'],
    },
    zip_safe = False
    )

