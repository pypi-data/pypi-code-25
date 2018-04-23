# Copyright 2018 Audios Ventures, Inc.
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
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

EXTRAS = {}
REQUIRES = []
with open('requirements.txt') as f:
    for line in f:
        line, _, _ = line.partition('#')
        line = line.strip()
        if ';' in line:
            requirement, _, specifier = line.partition(';')
            for_specifier = EXTRAS.setdefault(':{}'.format(specifier), [])
            for_specifier.append(requirement)
        else:
            REQUIRES.append(line)

with open('test-requirements.txt') as f:
    TESTS_REQUIRES = f.readlines()

setup(
    name='simpledeploy',
    version='0.2.3',
    packages=find_packages(),
    install_requires=REQUIRES,
    tests_require=TESTS_REQUIRES,
    extras_require=EXTRAS,
    author='Steven Crothers',
    author_email='crothers@simplecast.com',
    description='The simpledeploy system is a Python based Kubernetes deployment tool designed to work with Gitlab CI.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    license='Apache 2.0',
    keywords='gitlab gitlab-ci gitlab-api kubernetes kubernetes-deployment',
    url='https://github.com/audiosventures/simpledeploy',
    entry_points={
        'console_scripts': [
            'simpledeploy=simpledeploy:main'
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    project_urls={
        'Bug Tracker': 'https://github.com/audiosventures/simpledeploy/issues',
        'Documentation': 'https://github.com/audiosventures/simpledeploy/wiki',
        'Source Code': 'https://github.com/audiosventures/simpledeploy'
    }
)
