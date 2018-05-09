# Copyright (C) 2017 Allen Li
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

import os
import pathlib
import subprocess

import pytest


@pytest.fixture
def tmpdir(tmpdir_factory):
    tmpdir = tmpdir_factory.mktemp('tmpdir')
    return pathlib.Path(str(tmpdir))


@pytest.fixture
def gitdir(tmpdir):
    repo = tmpdir / 'repo'
    subprocess.run(['git', 'init', str(repo)])
    cwd = pathlib.Path.cwd()
    os.chdir(repo)
    try:
        subprocess.run(['git', 'config', 'user.name', 'Your Name'])
        subprocess.run(['git', 'config', 'user.email', 'you@example.com'])
        (repo / 'foo').write_text('foo\n')
        subprocess.run(['git', 'add', 'foo'])
        subprocess.run(['git', 'commit', '-m', 'foo'])
        yield repo
    finally:
        os.chdir(cwd)
