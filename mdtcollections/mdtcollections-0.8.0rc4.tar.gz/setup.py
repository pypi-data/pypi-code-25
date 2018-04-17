# Copyright 2016-2018 Autodesk Inc., 2018 project contributors
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

from setuptools import find_packages, setup
import versioneer

PACKAGE_NAME = 'mdtcollections'

CLASSIFIERS = """\
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: Apache Software License
Programming Language :: Python :: 3
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Operating System :: POSIX
Operating System :: Unix
Operating System :: MacOS
"""


with open('requirements.txt', 'r') as reqfile:
    requirements = [x.strip() for x in reqfile if x.strip()]


cmdclass = versioneer.get_cmdclass()

setup(
    name=PACKAGE_NAME,
    version=versioneer.get_version(),
    classifiers=CLASSIFIERS.splitlines(),
    packages=find_packages(),
    install_requires=[],
    url='http://github.com/avirshup/mdtcollections',
    cmdclass=cmdclass,
    license='Apache 2.0',
    author='Aaron Virshup',
    author_email='avirshup+pypi@gmail.com',
    description='Useful collection classes and utilities')
