from __future__ import print_function
import os


def build_is_triggered():
    """
    If a build is being triggered via Github directly (either by a comment, or
    automatically) then the ``ghprb`` will probably be involded. When that is
    the case, that plugin injects a wealth of environment variables, which can
    tell us if the build is really being handled by the plugin.
    """
    ghprb_env_vars = [
        'ghprbActualCommit', 'ghprbTriggerAuthor', 'ghprbTargetBranch',
        'ghprbTriggerAuthorLogin', 'ghprbCredentialsId', 'ghprbGhRepository',
    ]

    return all([bool(os.environ.get(var, False)) for var in ghprb_env_vars])


def construct_url():
    """
    Helper to join the different parts of Github's API url to be able to post
    the notification status
    """
    GITHUB_REPOSITORY = os.getenv('GITHUB_REPOSITORY')
    GITHUB_SHA = os.getenv('GITHUB_SHA')
    base_url = "https://api.github.com/repos/"
    repository = GITHUB_REPOSITORY.strip('/').strip('"')

    repo_url = os.path.join(base_url, repository)
    status_url = os.path.join(repo_url, 'statuses')
    full_url = os.path.join(status_url, GITHUB_SHA)
    print('request url: %s' % full_url)
    return full_url
