"""
GitHub module

This module extends the main PyGitHub class in order to add some extra
functionality.
"""

from git import Repo
from github import Github as PyGitHub
from github import Repository
from github.MainClass import DEFAULT_BASE_URL, DEFAULT_PER_PAGE, \
    DEFAULT_TIMEOUT


class GitHub(PyGitHub):
    """Object for communicating with GitHub and cloning repositories"""
    token: str

    def __init__(self, login_or_token=None, password=None,
                 base_url=DEFAULT_BASE_URL,
                 timeout=DEFAULT_TIMEOUT,
                 client_id=None, client_secret=None,
                 user_agent='PyGithub/Python',
                 per_page=DEFAULT_PER_PAGE,
                 api_preview=False):
        """Initializes a new GitHub object"""
        super().__init__(login_or_token, password, base_url, timeout,
                         client_id, client_secret,
                         user_agent, per_page,
                         api_preview)
        self.token = login_or_token

    def clone(self, repository: Repository, destination):
        """Clones a GitHub repository and returns a Git object"""
        environ = {}
        environ['GIT_ASKPASS'] = 'repository-updater-git-askpass'
        environ['GIT_USERNAME'] = self.token
        environ['GIT_PASSWORD'] = ''

        return Repo.clone_from(repository.clone_url, destination, None,
                               environ)
