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

import subprocess
from unittest import mock

import pytest

from mir import git


def test_GitEnvInterface_implemented_by_GitEnv():
    assert issubclass(git.GitEnv, git.GitEnvInterface)


def test_GitEnvInterface_implemented_by_str():
    assert issubclass(str, git.GitEnvInterface)


def test_GitEnvInterface_not_implemented_by_set():
    assert not issubclass(set, git.GitEnvInterface)


def test_GitEnv():
    e = git.GitEnv(gitdir='foo', worktree='bar')
    assert git.gitdir(e) == 'foo'
    assert git.worktree(e) == 'bar'


def test_git(gitdir):
    result = git.git(gitdir, ['status'])
    assert result.returncode == 0


def test_git_has_unpushed_changes_true(gitdir):
    subprocess.run(['git', 'branch', '-t', 'slave'])
    subprocess.run(['git', 'checkout', 'slave'])
    (gitdir / 'bar').touch()
    subprocess.run(['git', 'add', 'bar'])
    subprocess.run(['git', 'commit', '-m', 'bar'])
    assert git.has_unpushed_changes(gitdir)


def test_git_has_unpushed_changes_false(gitdir):
    assert not git.has_unpushed_changes(gitdir)


def test_git_has_unstaged_changes_true(gitdir):
    (gitdir / 'foo').write_text('bar\n')
    assert git.has_unstaged_changes(gitdir)


def test_git_has_unstaged_changes_false(gitdir):
    assert not git.has_unstaged_changes(gitdir)


def test_git_has_staged_changes_true(gitdir):
    (gitdir / 'foo').write_text('bar\n')
    subprocess.run(['git', 'add', 'foo'])
    assert git.has_staged_changes(gitdir)


def test_git_has_staged_changes_false(gitdir):
    assert not git.has_staged_changes(gitdir)


def test_git_get_current_branch(gitdir):
    assert git.get_current_branch(gitdir) == 'master'


def test_git_get_branches(gitdir):
    assert git.get_branches(gitdir) == ['master']


def test_git_save_branch(gitdir):
    subprocess.run(['git', 'branch', 'slave'])
    with git.save_branch(gitdir):
        subprocess.run(['git', 'checkout', 'slave'])
    branch = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                            stdout=subprocess.PIPE).stdout.decode().rstrip()
    assert branch == 'master'


def test_git_save_branch_should_be_quiet(capfd, gitdir):
    subprocess.run(['git', 'branch', '--quiet', 'slave'])
    with git.save_branch(gitdir):
        subprocess.run(['git', 'checkout', '--quiet', 'slave'])
    out, err = capfd.readouterr()
    assert not out
    assert not err


def test_git_save_branch_should_raise_when_restore_fails(gitdir):
    subprocess.run(['git', 'branch', 'slave'])
    with mock.patch.object(git, '_retry_wait', 0), \
         pytest.raises(subprocess.CalledProcessError), \
         git.save_branch(gitdir):
        subprocess.run(['git', 'checkout', 'slave'])
        subprocess.run(['git', 'branch', '-d', 'master'])


def test_git_save_worktree(gitdir):
    subprocess.run(['git', 'branch', 'slave'])
    (gitdir / 'foo').unlink()
    with git.save_worktree(gitdir):
        assert (gitdir / 'foo').exists()
    assert not (gitdir / 'foo').exists()


def test_git_save_worktree_should_be_quiet_with_change(capfd, gitdir):
    subprocess.run(['git', 'branch', '--quiet', 'slave'])
    (gitdir / 'foo').unlink()
    with git.save_worktree(gitdir):
        pass
    out, err = capfd.readouterr()
    assert not out
    assert not err


def test_git_save_worktree_should_be_quiet_without_change(capfd, gitdir):
    subprocess.run(['git', 'branch', '--quiet', 'slave'])
    with git.save_worktree(gitdir):
        pass
    out, err = capfd.readouterr()
    assert not out
    assert not err


def test_git_save_worktree_and_branch_saves_branch(gitdir):
    subprocess.run(['git', 'branch', 'slave'])
    with git.save_worktree_and_branch(gitdir):
        subprocess.run(['git', 'checkout', 'slave'])
    branch = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                            stdout=subprocess.PIPE).stdout.decode().rstrip()
    assert branch == 'master'
