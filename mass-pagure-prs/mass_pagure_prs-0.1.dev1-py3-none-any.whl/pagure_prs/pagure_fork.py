"""
"""

from libpagure import Pagure
from libpagure.exceptions import APIError


PAGURE_INSTANCE = 'https://src.fedoraproject.org'


class PagureForkException(Exception):

    """Base exception for PagureFork.
    """


class PagureFork(object):

    """A base class for package's fork on Pagure.
    """

    def __init__(self, pagure_repo_name, pagure_token,
                 pagure_user, logger, instance=PAGURE_INSTANCE):
        self.package_name = pagure_repo_name
        self.pagure_user = pagure_user
        self.logger = logger

        self.pagure = Pagure(
            pagure_repository=pagure_repo_name,
            instance_url=instance,
            pagure_token=pagure_token
        )

        self.fork_api = f"{self.pagure.instance}/api/0/fork"

    def do_fork(self):
        self.logger.debug(
            f'Creating fork of {self.package_name} for user '
            f'{self.pagure_user}')
        try:
            payload = {
                'wait': True,
                'namespace': 'rpms',
                'repo': self.package_name
            }
            response = self.pagure._call_api(
                self.fork_api, method='POST', data=payload)
            self.logger.debug(f"Fork created: {response}")
        except APIError as err:
            if 'already exists' in str(err):
                self.logger.info(
                    f'User {self.pagure_user} already has a fork '
                    f'of {self.package_name}')
            else:
                raise err
        except Exception as err:
            raise PagureForkException(
                f'Failed to create a fork for {self.package_name}. '
                f'Error: {err}')

    def get_ssh_git_url(self):
        """
        """
        git_urls_api = (
            f'{self.fork_api}/{self.pagure_user}/rpms/'
            f'{self.package_name}/git/urls')
        return_value = self.pagure._call_api(git_urls_api)
        return return_value['urls']['ssh']

    def create_pull_request(self, from_branch, to_branch,
                            title, description,
                            fas_user, fas_password):
        """Pagure API does not allow this yet.
        https://pagure.io/pagure/issue/2803
        """
        from .selenium_pagure_pr import create_pull_request
        url = (
            f'{self.pagure.instance}/login/?next={self.pagure.instance}'
            f'/fork/{self.pagure_user}/rpms/{self.package_name}'
            f'/diff/{to_branch}..{from_branch}')
        try:
            create_pull_request(
                url, title, description,
                fas_user, fas_password)
        except Exception as err:
            raise PagureForkException(
                f"Failed to create a PR for {self.package_name}. Error: {err}")

    def upstream_pr_with(self, **kwargs):
        request_url = (
            f'{self.pagure.instance}/api/0/rpms/{self.package_name}'
            '/pull-requests?status=All')
        return_value = self.pagure._call_api(request_url)
        for request in return_value['requests']:
            if any(value == request[key] for key, value in kwargs.items()):
                return request

    def has_upstream_pr_with(self, **kwargs):
        request = self.upstream_pr_with(**kwargs)
        if request:
            return (
                f'{self.pagure.instance}/rpms/{self.package_name}'
                f'/pull-request/{request["id"]}')

    def merge_upstream_pr(self, pr_id):
        try:
            self.pagure.merge_request(pr_id)
            self.logger.debug(f"PR merged")
        except Exception as err:
            raise PagureForkException(
                f"Failed to merge a PR {pr_id}. Error: {err}")
