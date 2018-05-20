from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='gamification',
    version='0.0.0',
    description='Some console games',
    long_description=long_description,
    url='https://github.com/monzita/gamification',
    author='Monika Ilieva',
    author_email='hidden@hidden.com',
    license='MIT',
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Topic :: Games/Entertainment :: Arcade',
      'Topic :: Games/Entertainment :: Board Games',
      'Topic :: Games/Entertainment :: First Person Shooters',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python :: 3.6'
    ],

    keywords='board game gamification games cli',
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'venv']),
)