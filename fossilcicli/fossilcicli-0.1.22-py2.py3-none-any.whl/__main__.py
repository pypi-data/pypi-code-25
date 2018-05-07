import sys
import argparse
import subprocess

from . import commands
from . import git_flow
from . import env
from . import utils

'''
This tool is intended to build and deploy services on Bitbucket piplines
by using GitFlow.
'''


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

    generate_doc_parser = cmd_subparser.add_parser('generate_doc')
    generate_doc_parser.add_argument(
        '-l', '-language', dest="language", required=True, choices=['go'], help='the language of project')
    generate_doc_parser.add_argument(
        '-o', '-out', dest="out", required=True, help='the output doc file')

    push_doc_parser = cmd_subparser.add_parser('push_doc')
    setup_push_doc_parser(push_doc_parser)

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
    elif kwargs['cmd'] == 'push_doc':
        commands.push_doc(**kwargs)
    elif kwargs['cmd'] == 'generate_doc':
        commands.generate_doc(**kwargs)


def setup_push_doc_parser(parser):
    parser.add_argument('-v', '--version', dest="version",
                        help='the version of API document')
    parser.add_argument('-f', '--file', dest="file",
                        required=True, help='the path of Swagger file in Json format')
    parser.add_argument('-k', '--key', dest="key",
                        help='the authentication key for pushing the document')
    parser.add_argument('-u', '--url', dest="url",
                        help='the url to push document')
    parser.add_argument('-e', '--env', dest="env",
                        help='the url to push document')
    parser.add_argument('-p', '--project', dest="project",
                        help='the project name')


if __name__ == '__main__':
    main()
