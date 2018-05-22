#!/usr/bin/env python

from setuptools import setup
setup(name='reedmuller',
      version='1.1.0',
      description='Reed-Muller code encoding and decoding',
      author='Sebastian Raaphorst',
      author_email='srcoding@gmail.com',
      url='https://github.com/sraaphorst/reedmuller',
      packages=['reedmuller'],
      long_description="""
          The reedmuller library comprises an implementation of Reed-Muller code
          encoding and decoding with Python 2 or 3.
      """,
      classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Mathematics',
        ],
      keywords='mathematics combinatorics codes reedmuller reed-muller',
      license='Apache 2.0'
      )

