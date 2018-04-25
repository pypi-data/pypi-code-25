import os
import sys

from tambo import Transport
from github_status import create, listing, conf
import github_status


class Status(object):
    _help = """
github-status: A utility to easily send status updates for commits on Github.
Only useful when a PR is not getting triggered via a Github hook, which will be
updated via ghprb (Github Pull Request Builder)


Version: %s

Sub Commands:
%s

Github Environment Variables:

GITHUB_REPOSITORY       The url part of the repo, like ceph/ceph
GITHUB_SHA              A commit SHA that will receive the update
GITHUB_OAUTH_TOKEN      Generated TOKEN to authenticate to Github
GITHUB_STATUS_CONTEXT   The "title" part of the status, like "docs"
GITHUB_STATUS_STARTED   The 'started' text that will change next to the 'title' (context)
GITHUB_STATUS_SUCCESS   The 'success' text that will change next to the 'title' (context)
GITHUB_STATUS_FAILURE   The 'failure' text that will change next to the 'title' (context)
GITHUB_STATUS_ERROR     The 'error' text that will change next to the 'title' (context)
GITHUB_STATUS_STATE     The state for the sha1, one of: 'success', 'error', 'failure', or 'pending'

Build Environment Variables:

BUILD_URL               A url that points to the actual full url for the build
PARENT_BUILD_URL        Optional parent url where actual build happened
    """
    mapper = {'create': create.Create, 'list': listing.List}
    required_env_vars = [
        'GITHUB_REPOSITORY',
        'GITHUB_SHA',
        'GITHUB_OAUTH_TOKEN',
        'GITHUB_STATUS_CONTEXT',
        'GITHUB_STATUS_STARTED',
        'GITHUB_STATUS_SUCCESS',
        'GITHUB_STATUS_FAILURE',
        'GITHUB_STATUS_ERROR',
        'GITHUB_STATUS_STATE',
        'BUILD_URL']

    def __init__(self, argv=None, parse=True):
        if argv is None:
            argv = sys.argv
        conf['env'] = dict(
            (k, os.getenv(k)) for k in self.required_env_vars if os.getenv(k) is not None)

        # Go through all the vars again, and make sure that quotes are trimmed. Otherwise
        # the JSON loading/dumping will add them like u'"foo"' instead of u'foo'
        for k, v in conf['env'].items():
            conf['env'][k] = v.replace('"', '').replace("'", '')
        if parse:
            self.main(argv)

    def help(self):
        sub_help = '\n'.join(['%-19s %s' % (
            sub.__name__.lower(), getattr(sub, 'help_menu', ''))
            for sub in self.mapper.values()])
        return self._help % (github_status.__version__, sub_help)

    def main(self, argv):
        parser = Transport(argv, mapper=self.mapper,
                           check_help=False,
                           check_version=False)
        parser.catch_help = self.help()
        parser.catch_version = github_status.__version__
        parser.mapper = self.mapper
        if len(argv) <= 1:
            return parser.print_help()
        parser.dispatch(with_exit=True)
        parser.catches_help()
        parser.catches_version()
