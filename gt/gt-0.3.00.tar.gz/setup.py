#!/usr/bin/env python3

from distutils.core import setup
setup(name='gt',
        version='0.3.00',
        author='Raheman Vaiya',
        author_email='r.vaiya@gmail.com',
        url='http://gitlab.com/rvaiya/gt',
        keywords='git github gitlab ssh cli console management',
        long_description=open('README.rst').read(),
        packages=['gt.sources'],
        scripts=['bin/gt'],
        classifiers=[
            'Programming Language :: Python :: 3',
            'Development Status :: 3 - Alpha'
            ],
      install_requires=['requests', 'bs4']
)
