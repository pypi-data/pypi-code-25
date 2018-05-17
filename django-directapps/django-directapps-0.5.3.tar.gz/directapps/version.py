# -*- coding: utf-8 -*-
#
#   Copyright 2016 Grigoriy Kramarenko <root@rosix.ru>
#
#   This file is part of DirectApps.
#
#   DirectApps is free software: you can redistribute it and/or
#   modify it under the terms of the GNU Affero General Public License
#   as published by the Free Software Foundation, either version 3 of
#   the License, or (at your option) any later version.
#
#   DirectApps is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public
#   License along with DirectApps. If not, see
#   <http://www.gnu.org/licenses/>.
#

from __future__ import unicode_literals
import os
import subprocess
from datetime import datetime


def get_version(version, repo_dir=None):
    "Returns a PEP 386-compliant version number from VERSION."
    version = get_complete_version(version)

    # Now build the two parts of the version number:
    # major = X.Y[.Z]
    # sub = .devN - for pre-alpha releases
    #     | {a|b|c}N - for alpha, beta and rc releases

    major = get_major_version(version)

    sub = ''
    if version[3] == 'alpha' and version[4] == 0:
        changeset = get_vcs_changeset(repo_dir)
        if changeset:
            sub = '.dev%s' % changeset

    elif version[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'c'}
        sub = mapping[version[3]] + str(version[4])

    return str(major + sub)


def get_docs_version(version):
    version = get_complete_version(version)
    if version[3] != 'final':
        return 'dev'
    else:
        return '%d.%d' % version[:2]


def get_major_version(version):
    "Returns major version from VERSION."
    version = get_complete_version(version)
    parts = 2 if version[2] == 0 else 3
    major = '.'.join(str(x) for x in version[:parts])
    return major


def get_complete_version(version):
    """
    Returns a tuple of the directapps version. If version argument
    is non-empty, then checks for correctness of the tuple provided.
    """
    if not version:
        return (0, 0, 1, 'alpha', 0)
    assert len(version) == 5
    assert version[3] in ('alpha', 'beta', 'rc', 'final')
    return version


def get_hg_timestamp(repo_dir):
    "Returns a timestamp of the latest Mercurial changeset."
    hg_log = subprocess.Popen(
        'hg tip --template "{date|hgdate}"',
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True, cwd=repo_dir, universal_newlines=True
    )
    stamp = hg_log.communicate()[0]
    try:
        stamp = stamp.split(' ')[0]
        stamp = datetime.utcfromtimestamp(int(stamp))
    except ValueError:
        stamp = None
    return stamp


def get_git_timestamp(repo_dir):
    "Returns a timestamp of the latest Git changeset."
    git_log = subprocess.Popen(
        'git log --pretty=format:%ct --quiet -1 HEAD',
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True, cwd=repo_dir, universal_newlines=True
    )
    stamp = git_log.communicate()[0]
    try:
        stamp = datetime.utcfromtimestamp(int(stamp))
    except ValueError:
        stamp = None
    return stamp


def get_git_hashcode(repo_dir):
    "Retunrs Git commit short id."
    try:
        ref = open(os.path.join(repo_dir, '.git', 'HEAD'), 'r').readline()
    except IOError:
        return None
    ref = ref.replace('ref: ', '').replace('\n', '')
    if ref.startswith('refs'):
        code = open(os.path.join(repo_dir, '.git', ref), 'r').readline()
        if code:
            return code[:8]
    return None


def get_vcs_changeset(repo_dir):
    "Returns a numeric identifier of the latest VCS changeset."
    if not repo_dir:
        path = os.path.abspath(os.path.realpath(__file__))
        repo_dir = os.path.dirname(os.path.dirname(path))
    timestamp = get_git_timestamp(repo_dir)
    if not timestamp:
        timestamp = get_hg_timestamp(repo_dir)
    if timestamp:
        return timestamp.strftime('%Y%m%d%H%M%S')
    # In the servers maybe not work subprocess, returns Git hashcode
    return get_git_hashcode(repo_dir)
