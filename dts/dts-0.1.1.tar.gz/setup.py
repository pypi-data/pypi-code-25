# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dts',  # Required

    version='0.1.1',  # Required

    description='Generate sequence of datatimes, like seq',  # Required
    long_description='# Generate sequence of datatimes, like seq',  # README.md
    long_description_content_type='text/markdown', 

    url='https://github.com/KwangYeol/dts',
    author='Kwangyeol Ryu',
    author_email='kwangyeolryu@gmail.com',

    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='seq datetime generator',

    py_modules=["dts"],
    # packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required

    install_requires=[],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # `pip` to create the appropriate form of executable for the target
    # platform.
    scripts=['dts/cli.py'],
    entry_points={  # Optional
        'console_scripts': [
            'dts=cli:main',
        ],
    },

    project_urls={  # Optional
        'Bug Reports': 'https://github.com/KwangYeol/dts/issues',
        'Source': 'https://github.com/KwangYeol/dts',
    },
)