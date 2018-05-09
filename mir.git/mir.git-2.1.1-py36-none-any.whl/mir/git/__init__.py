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

"""Python interface to Git.

The main member of this module is the git() generic function.

The most general git() method is for GitEnv instances, which describes a
Git invocation environment.

Most users can use the string git() method, which will be interpreted as
the working tree for a standard non-bare Git repo.

If you have your own Git wrappers, you can register a git() method for
it so git() can accept them as environments transparently.

Members:

git() -- All-purpose generic function interface to Git
GitEnv -- Git invocation environment
default_encoding -- Default encoding for subprocesses

get_current_branch()
get_branches()
has_staged_changes()
has_unpushed_changes()
has_unstaged_changes()
save_branch()
save_worktree()
"""

import abc
import contextlib
import functools
import logging
import os
import random
import subprocess
import time
from typing import NamedTuple

__version__ = '2.1.1'

logger = logging.getLogger(__name__)
default_encoding = 'utf-8'


class GitEnvInterface(abc.ABC):

    """Abstract base class for Git environment implementations."""

    @classmethod
    def __subclasshook__(cls, C):
        return (cls._has_implementation(gitdir, C)
                and cls._has_implementation(worktree, C))

    @staticmethod
    def _has_implementation(f, C):
        default = f.dispatch(object)
        return f.dispatch(C) is not default


class GitEnv(NamedTuple):
    gitdir: str
    worktree: str


@functools.singledispatch
def gitdir(gitenv) -> str:
    """Get GIT_DIR."""
    raise NotImplementedError


@functools.singledispatch
def worktree(gitenv) -> str:
    """Get GIT_WORK_TREE."""
    raise NotImplementedError


@gitdir.register(GitEnv)
def _gitdir_GitEnv(gitenv):
    return gitenv.gitdir


@worktree.register(GitEnv)
def _worktree_GitEnv(gitenv):
    return gitenv.worktree


@gitdir.register(os.PathLike)
@gitdir.register(str)
def _gitdir_str(worktree):
    return os.path.join(os.fspath(worktree), '.git')


@worktree.register(os.PathLike)
@worktree.register(str)
def _worktree_str(worktree):
    return os.fspath(worktree)


def git(gitenv, args, **kwargs):
    """Run a Git command.

    gitenv is a GitEnv, or some representation of a Git environment that
    has methods for gitdir() and worktree().  args and kwargs are passed
    to subprocess.run().

    Returns a CompletedProcess.
    """
    kwargs.setdefault('encoding', default_encoding)
    kwargs['env'] = process_env(gitenv, kwargs.get('env', os.environ))
    return subprocess.run(['git', *args], **kwargs)


def process_env(gitenv: GitEnv, env: dict):
    """Get process environment."""
    env = env.copy()
    env['GIT_DIR'] = gitdir(gitenv)
    env['GIT_WORK_TREE'] = worktree(gitenv)
    return env


def has_unpushed_changes(gitenv) -> bool:
    """Return True if the Git repo has unpushed changes."""
    result = git(gitenv, ['rev-list', '-n', '1', 'HEAD@{u}..HEAD'],
                 stdout=subprocess.PIPE)
    return bool(result.stdout)


def has_staged_changes(gitenv) -> bool:
    """Return True if the Git repo has staged changes."""
    result = git(gitenv, ['diff-index', '--quiet', '--cached', 'HEAD'])
    return result.returncode != 0


def has_unstaged_changes(gitenv) -> bool:
    """Return True if the Git repo has unstaged changes."""
    result = git(gitenv, ['diff-index', '--quiet', 'HEAD'])
    return result.returncode != 0


def get_current_branch(gitenv) -> str:
    """Return the current Git branch."""
    return git(gitenv, ['rev-parse', '--abbrev-ref', 'HEAD'],
               stdout=subprocess.PIPE).stdout.rstrip()


def get_branches(gitenv) -> list:
    """Return a list of a Git repository's branches."""
    proc = git(gitenv, ['for-each-ref', '--format=%(refname)', 'refs/heads/'],
               check=True, stdout=subprocess.PIPE)
    output = proc.stdout.splitlines()
    start = len('refs/heads/')
    return [line.rstrip()[start:] for line in output]


_retry_wait = 0.1


def _cmd_retry(func):
    @functools.wraps(func)
    def retrier(*args, **kwargs):
        wait = _retry_wait
        err = Exception()
        for _ in range(3):
            try:
                return func(*args, **kwargs)
            except subprocess.CalledProcessError as e:
                err = e
                time.sleep(random.random() * wait)
                wait *= 2
        raise err
    return retrier


class save_branch:

    """Context manager for saving and restoring the current Git branch."""

    def __init__(self, gitenv):
        self._gitenv = gitenv
        self.starting_branch = None

    def __enter__(self):
        self.starting_branch = get_current_branch(self._gitenv)
        return self

    @_cmd_retry
    def __exit__(self, exc_type, exc_val, exc_tb):
        git(self._gitenv, ['checkout', '--quiet', '--force', self.starting_branch],
            check=True)


class save_worktree:

    """Context manager for saving and restoring the worktree."""

    def __init__(self, gitenv):
        self._gitenv = gitenv
        self._stash = ''

    def __enter__(self):
        # BUG: https://public-inbox.org/git/CAJr1M6eS0jY22=0nvV41uDybcHUdjBv8CgRhHmBNFM=Z0J9YCA@mail.gmail.com/
        proc = git(self._gitenv, ['-C', worktree(self._gitenv), 'stash', 'create'],
                   check=True,
                   stdout=subprocess.PIPE)
        self._stash = proc.stdout.rstrip()
        logger.debug(f'Created stash {self._stash!r}')
        git(self._gitenv, ['reset', '--hard', '--quiet', 'HEAD'], check=True)
        return self

    @_cmd_retry
    def __exit__(self, exc_type, exc_val, exc_tb):
        # If there were no changes to stash, this is the empty string.
        if self._stash:
            git(self._gitenv, ['-C', worktree(self._gitenv),
                               'stash', 'apply', '--quiet', self._stash], check=True)


@contextlib.contextmanager
def save_worktree_and_branch(gitenv):
    """Context manager for saving and restoring the worktree and branch."""
    with save_worktree(gitenv):
        with save_branch(gitenv) as branch_context:
            yield branch_context
