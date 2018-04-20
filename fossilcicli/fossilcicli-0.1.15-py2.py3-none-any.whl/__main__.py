import sys
import argparse
import subprocess

from . import commands
from . import git_flow
from . import env
from . import utils


def main():
    '''Setup hook function for excepthook'''
    sys.excepthook = utils.my_except_hook

    '''Setup un buffered stdout'''
    sys.stdout = utils.UnBuffered(sys.stdout)

    '''Login ecr'''
    subprocess.check_output(
        "aws ecr get-login --no-include-email", shell=True)
    subprocess.check_output(
        "eval $(aws ecr get-login --no-include-email)", shell=True)

    parser = argparse.ArgumentParser()
    cmd_subparser = parser.add_subparsers(dest='cmd')
    cmd_subparser.add_parser('test')
    cmd_subparser.add_parser('build')
    cmd_subparser.add_parser('deploy')

    kwargs = vars(parser.parse_args())

    deployment_info = git_flow.DeploymentInfo(
        env.FOSSILCI_BRANDS, env.FOSSILCI_BRANCHES_BRANDS, env.FOSSILCI_JOBS, env.FOSSILCI_JOBS_NAME_MAPPINGS, env.FOSSILCI_DEPLOY_ENV)

    deployment_info.parse(env.GIT_BRANCH, env.GIT_TAG, env.GIT_COMMIT,
                          env.BITBUCKET_BUILD_NUMBER, env.BITBUCKET_REPO_SLUG)
    if kwargs['cmd'] == 'test':
        commands.test(deployment_info=deployment_info, **kwargs)
    elif kwargs['cmd'] == 'build':
        commands.build(deployment_info=deployment_info, **kwargs)
    elif kwargs['cmd'] == 'deploy':
        commands.deploy(deployment_info)


if __name__ == '__main__':
    main()
