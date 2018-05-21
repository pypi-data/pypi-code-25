from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
print(find_packages('UO', exclude=('setup.py')))
setup(
    name='UO-test-functions',
    version='1.0.3',
    description='An Unconstrained Optimization Test Functions Collection',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/SupremaLex/UO-test-funcs/',
    author='George Lutsenko',
    author_email='georglutsenko@gmail.com',
	
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
	'Intended Audience :: Education',
        'Topic :: Scientific/Engineering :: Mathematics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='minimization unconstrained-optimization test-functions optimization',
    packages=['UO.test_functions'],#find_packages('UO',exclude=('setup.py')),
    package_data={'UO': ['ChangeLog'],},
    install_requires=['sympy', 'numpy', 'matplotlib'],
    project_urls={
        'Bug Reports': 'https://github.com/SupremaLex/UO-test-funcs/issues',
        'Source': 'https://github.com/SupremaLex/UO-test-funcs/',
    },
)


