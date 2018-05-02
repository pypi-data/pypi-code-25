"""
"""

import subprocess
import time


class LocalRepoException(Exception):

    """Base exception class for LocalRepo.
    """


class LocalRepo(object):

    """A base class for package's local repository.
    """

    def __init__(self, package_name, dirname, logger):
        self.package_name = package_name
        self.dirname = dirname
        self.logger = logger

        self.__specfile = None

    @property
    def specfile(self):
        if not self.__specfile:
            self.__specfile, = self.dirname.glob('*.spec')
        return self.__specfile

    # Fedpkg commands.
    def clone(self):
        self.logger.debug(f'Cloning {self.package_name} into {self.dirname}')
        try:
            subprocess.check_output(
                ['fedpkg', 'clone', self.package_name, self.dirname],
                stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            if 'already exists and is not an empty directory' in str(err.output):
                # The repo was already cloned, so just reset it to master
                # and pull recent changes.
                subprocess.check_output(
                    ['git', 'reset', '--hard', 'master'],
                    cwd=self.dirname)
                subprocess.check_output(
                    ['git', 'pull', '--rebase', 'origin', 'master'],
                    cwd=self.dirname)

    def create_srpm(self):
        subprocess.call(
            ['fedpkg', '--release', 'master', 'srpm'],
            cwd=self.dirname, stdout=subprocess.PIPE)
        srpm_name = self.dirname.glob('*.src.rpm')
        return srpm_name

    def run_mockbuild(self):
        try:
            output = subprocess.check_output(
                ['fedpkg', '--release', 'master', 'mockbuild'],
                cwd=self.dirname, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            self.logger.error(
                f'Mock build did not pass for {self.package_name}. '
                f'Error: {err.output}')
            raise err
        return output

    def run_koji_scratch_build(self):
        try:
            output = subprocess.check_output(
                ['fedpkg', '--release', 'master',
                 'build', '--scratch', '--srpm'],
                cwd=self.dirname)
        except subprocess.CalledProcessError as err:
            self.logger.error(
                f'Failed to run Koji scratch build for {self.dirname}. '
                f'Error: {err.output}')
            raise err
        return output

    def bump_spec(self, comment):
        subprocess.check_call(
            ['rpmdev-bumpspec', '-c', comment, self.specfile])

    def apply_patch(self, patch_path):
        subprocess.check_output(
            ['git', 'apply', patch_path],
            cwd=self.dirname, stderr=subprocess.STDOUT)

    # Git commands.
    def git_last_commit(self):
        output = subprocess.check_output(
            ['git', 'log', '-1', '--pretty=format:%ct'],
            cwd=self.dirname)
        return output

    def create_branch(self, branch_name):
        subprocess.check_output(
            ['git', 'checkout', '-B', branch_name],
            cwd=self.dirname)

    def show_diff(self, filename):
        subprocess.call(
            ['git', '--no-pager', 'diff', filename],
            cwd=self.dirname)

    def add_to_git_remotes(self, remote_name, url):
        try:
            subprocess.check_output(
                ['git', 'remote', 'add', remote_name, url],
                cwd=self.dirname,
                stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            if 'already exists' in str(err.output):
                self.logger.info('Fork already added to remotes')
                pass
            else:
                raise err
        except Exception as err:
            raise LocalRepoException(
                f"Failed to add to git remotes. Error: {err}")

    def git_add(self, filename):
        subprocess.check_output(
            ['git', 'add', filename.relative_to(self.dirname)],
            cwd=self.dirname, stderr=subprocess.STDOUT)

    def git_commit(self, message):
        subprocess.check_output(
            ['git', 'commit', '-m', message],
            cwd=self.dirname, stderr=subprocess.STDOUT)

    def git_push(self, remote_name, branch_name):
        """Push local changes to a branch of fork.
        """
        # On Pagure you can not immediately push to the fork.
        # And there is no api call to check that the fork is ready.
        # So here is a hack: try to do it at least 4 times with an interval
        # in 3 minutes. Oh well.
        for attempt in range(4):
            try:
                self.logger.debug(
                    f'Trying to push changes to fork (Attempt {attempt})')
                subprocess.check_output(
                    ['git', 'push', '-f', remote_name, branch_name],
                    cwd=self.dirname,
                    stderr=subprocess.STDOUT)
                break
            except subprocess.CalledProcessError as err:
                if 'DENIED by fallthru' in str(err.output):
                    self.logger.debug('Will sleep for 3 minutes')
                    time.sleep(60 * 3)
            except Exception as err:
                raise LocalRepoException(
                    f"Failed to push to a fork. Error: {err}")
        else:
            raise LocalRepoException(
                'Could not push to fork, it is still not available')
        self.logger.debug("Successfully pushed to a fork")
