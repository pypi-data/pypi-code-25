# Copyright 2018 The NLP Odyssey Authors.
# Copyright 2018 Marco Nicola <marconicola@disroot.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages
from os import path

base_path = path.abspath(path.dirname(__file__))

with open(path.join(base_path, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='colonel',
    version='1.0.0',
    license='Apache-2.0',
    description='A Python 3 library for handling CoNLL data formats',
    long_description=long_description,
    url='https://github.com/nlpodyssey/colonel',
    author='The NLP Odyssey Authors',
    maintainer='Marco Nicola',
    maintainer_email='marconicola@disroot.org',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Utilities'
    ],
    keywords='conll conllu dependency parsing',
    packages=find_packages(exclude=['tests', 'tests.*']),
    python_requires='>=3.6, <4',
    install_requires=[
        'ply>=3,<4'
    ]
)
