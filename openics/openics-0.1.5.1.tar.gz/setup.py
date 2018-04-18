
"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='openics',  # Required
    version='0.1.5.1',  # Required
    # Required
    description='iCreativeFactor\'s library for autonomous system.',
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://github.com/iCreativeFactor/openics',  # Optional
    author='iCreativeFactor',  # Optional
    author_email='adadesions@gmail.com',  # Optional
    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='openics, machine learning, vision, ai, \
    icreativefactor, adafactor, icreativesystem, open_ics',  # Optional
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required
    install_requires=['numpy', 'opencv-python'],  # Optional
    python_requires='>=3',
    extras_require={  # Optional
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    # entry_points={  # Optional
    #     'console_scripts': [
    #         'openics=openics:main',
    #     ],
    # },
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/iCreativeFactor/openics/issues',
        'Source': 'https://github.com/iCreativeFactor/openics',
    },
)
