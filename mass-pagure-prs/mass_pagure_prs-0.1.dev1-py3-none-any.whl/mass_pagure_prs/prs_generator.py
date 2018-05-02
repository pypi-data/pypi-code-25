"""
"""
import logging
import pathlib
import tempfile

from .local_repo import LocalRepo
from .pagure_fork import PagureFork


def get_logger(name=__name__, level=logging.DEBUG):
    logging.basicConfig(format='%(levelname)s: %(message)s')
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger


class BasePRsGeneratorError(Exception):

    """Base exception for PRsGenerator.
    """


class BasePRsGenerator(object):

    """A base class for Pagure PRs generation.
    """

    def __init__(
            self,
            packages_filename,
            output_dirname=None,
            dry_run=False,
            pagure_token=None,
            pagure_user=None,
            fas_user=None,  # Remove with Pagure 4.0
            fas_password=None,  # Remove with Pagure 4.0
            logger=get_logger()):
        """
        Modifies spec files for a list of given packages
        and creates Pagure PRs for them from a fork.

        Args:
            packages_filename (str): A file name  with a list of packages
                to process (separated by new line).
            output_dirname (str) Directory path to clone packages, process
                specc files and do the tests.
                Optional, if not supplied a temporary directory will be
                created.
            dry_run (bool): In a dry run the pagure related operations will
                not be done. Only a diff of specfile changes will be shown,
                but the fork and pull request will not be created.
                Optional, defaults to False
            pagure_token (str): A token generated for Pagure operations.
                Optional, needed only in non dry run.
            pagure_user (str): A Pagure user, which will be used to fork
                the project and create a PR on Pagure.
                Optional, needed only in non dry run.
            fas_user (str): FAS username (needed for selenium PR).
                Optional, needed only in non dry run. Will not be needed
                with Pagure 4.0
            fas_password (str): FAS username (needed for selenium PR).
                Optional, needed only in non dry run. Will not be needed
                with Pagure 4.0
            logger (str): Configured logger.
                Optional, if not provided a logger with DEBUG level will
                be created and used.
        """
        self.logger = logger
        self.packages_filename = packages_filename
        self.dirname = output_dirname or tempfile.mkdtemp()

        self.dry_run = dry_run
        self.pagure_user = pagure_user
        self.pagure_token = pagure_token

        self.fas_user = fas_user  # Remove with Pagure 4.0
        self.fas_password = fas_password  # Remove with Pagure 4.0

        self.__pr_data = {}

        if not dry_run and not (pagure_token and pagure_user):
            raise BasePRsGeneratorError(
                'Please provide both pagure_token and pagure_user,'
                'if you intend to use non dry run.')

    def modify_spec(self, specfile):
        """Modify a spec file and return a modified version.

        Args:
            specfile (str): Spec file as a string.

        Return:
            (str) A modified spec file.
        """
        raise NotImplementedError()

    def check_mock_build_results(self, output):
        """Given the output of the mock build check the result.

        Args:
            output (str): The output of the mock build as a string
                for parsing and processing.
        Raise:
            An Exception if the output is not expected.
        Return: None
        """
        pass

    def check_koji_scratch_build_results(self, output):
        """Given the output of the koji scratch build check the result.

        Args:
            output (str): The output of the Koji scratch build as a string
                for parsing and processing.
        Raise:
            An Exception if the output is not expected.
        Return: None
        """
        pass

    def configure(self, git_branch, changelog_entry, commit_message,
                  pr_title, pr_description):
        """Set the name of the git branch and texts for the PR.

        Args:
            git_branch (str): Name of the branch to be created on Pagure
                fork, from which the PR will be opened.
            changelog_entry (str): A spec file changelog entry.
            commit_message (str): A Git commit message.
            pr_title (str): A title for the Pagure PR.
            pr_description (str): A description for the Pagure PR.
        """
        self.__pr_data = {
            'git_branch': git_branch,
            'changelog_entry': changelog_entry,
            'commit_message': commit_message,
            'pr_title': pr_title,
            'pr_description': pr_description,
        }

    def set_pr_description(self, pr_description):
        self.__pr_data['pr_description'] = pr_description

    def set_pr_title(self, pr_title):
        self.__pr_data['pr_title'] = pr_title

    def __do_mock_build(self, local_repo):
        """
        """
        self.logger.debug('Running mock build')
        output = local_repo.run_mockbuild()
        self.logger.debug(f'Mock build completed. Output: {output}')
        self.check_mock_build_results(output)

    def __do_koji_scratch_build(self, local_repo):
        """
        """
        self.logger.debug('Running a koji build')
        output = local_repo.run_koji_scratch_build()
        self.logger.debug(f'Koji scratch build completed. Output: {output}')
        self.check_koji_scratch_build_results(output)

    def __fix_specfile(self, specfile):
        """Fix a spec file.

        Args:
            specfiles (str): A spec file path.
        Return:
            (bool) True if fixed, False if no changes were made.
        """
        with open(specfile, 'rt') as f:
            spec = f.read()

        new_spec = self.modify_spec(spec)

        with open(specfile, 'wt') as out:
            out.write(new_spec)

        return spec != new_spec

    def run(self, do_mock_build=True, do_koji_scratch_build=False):
        """Do changes and open Pagure PRs.

        Take packages from a file supplied and for each:
        - clone the spec file to the temporary directory or the one supplied
        - modify the spec file
        - build an srpm
        - run a mock build (optional)
        - run a Koji scratch build (optional)
        - create a fork of the repo in Pagure (for a specified user)
        - push changes to a fork
        - create a Pagure Pull Request from fork to upstream

        Args:
            do_mock_build (bool): Run a mock build after the changes were made
                to the package spec file. Results check can be customized
                by overriding `check_mock_build_results` method.
                Defaults to True.
            do_koji_scratch_build (bool): Run a Koji scratch build after the
                changes were made to the package spec file. Results check can
                be customized by overriding `check_koji_scratch_build_results`
                method.
                Defaults to False.
        Raise:
            BasePRsGeneratorError if anything goes wrong.
        Return:
            (list of str) A list of links to opened PRs.
        """
        if not self.__pr_data:
            raise BasePRsGeneratorError(
                'Please configure PR data (texts for commit and changelog '
                'message, PR description and title etc). You can do it via '
                '`BasePRsGenerator.configure` method.')

        with open(self.packages_filename, 'rt') as f:
            packages = f.read().splitlines()

        fixed_packages = []
        problem_packages = []
        opened_pr_links = []

        self.logger.debug(f'Cloning packages into {self.dirname}')

        for package_name in packages:
            try:
                local_repo = LocalRepo(
                    package_name,
                    pathlib.Path(f'{self.dirname}/{package_name}'),
                    self.logger)

                local_repo.clone()
                local_repo.create_branch(self.__pr_data['git_branch'])

                spec_fixed = self.__fix_specfile(local_repo.specfile)
                if not spec_fixed:
                    raise BasePRsGeneratorError(
                        'No changes made to the spec file. '
                        'The package might already be fixed')

                local_repo.bump_spec(self.__pr_data['changelog_entry'])
                local_repo.show_diff(local_repo.specfile)

                if not self.dry_run:
                    # Create a fork before testing to avoid
                    # waiting the fork to be ready to be pushed to.
                    pagure_fork = PagureFork(
                        package_name,
                        self.pagure_token,
                        self.pagure_user,
                        self.logger)

                    pagure_fork.do_fork()
                    fork_url = pagure_fork.get_ssh_git_url()

                # QA.
                local_repo.create_srpm()

                if do_mock_build:
                    self.__do_mock_build(local_repo)

                if do_koji_scratch_build:
                    self.__do_koji_scratch_build(local_repo)

                # All good at this point. Go ahead and push.
                if not self.dry_run:
                    # Use username as a name for fork remote if not provided.
                    remote_name = self.pagure_user

                    local_repo.add_to_git_remotes(remote_name, fork_url)
                    local_repo.git_add(local_repo.specfile)
                    local_repo.git_commit(self.__pr_data['commit_message'])
                    local_repo.git_push(
                        remote_name, self.__pr_data['git_branch'])
                    # If the PR is already there, then the script is being run
                    # the second time, and just pushing to a fork is enough.
                    pr = pagure_fork.has_upstream_pr_with(
                        title=self.__pr_data['pr_title'],
                        branch_from=self.__pr_data['git_branch'])
                    if pr:
                        self.logger.info(f"The PR was already opened: {pr}")
                        continue

                    pagure_fork.create_pull_request(
                        from_branch=self.__pr_data['git_branch'],
                        to_branch='master',
                        title=self.__pr_data['pr_title'],
                        description=self.__pr_data['pr_description'],
                        fas_user=self.fas_user,  # Remove with Pagure 4.0
                        fas_password=self.fas_password)  # Remove with Pagure 4.0

                    pr = pagure_fork.has_upstream_pr_with(
                        title=self.__pr_data['pr_title'],
                        branch_from=self.__pr_data['git_branch'])
                    opened_pr_links.append(pr)

            except Exception as err:
                self.logger.error(
                    f"Failed to fix a package {package_name}. Error: {err}")
                problem_packages.append(package_name)
                continue

            fixed_packages.append(package_name)

        result = (
            '\n\nRESULTS:\n'
            f'The following {len(problem_packages)} packages had some issue '
            f'and were not pushed:\n{problem_packages}\n.'
            f'The following {len(fixed_packages)} packages were successfully '
            f'fixed:\n{fixed_packages}\n.'
        )
        self.logger.info(result)

        if not self.dry_run:
            return opened_pr_links
        else:
            return []
