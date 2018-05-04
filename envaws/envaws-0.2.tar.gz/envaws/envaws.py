#!/usr/bin/python3
"""
Run application with environment loaded from AWS SSM.
Inspired by envconsul.

Usage:

    ./envaws.py REGION PREFIX APP_NAME APP_ARG_1 ... APP_ARG_N

Example:

    ./envaws.py us-east-1 /dev/someservice /bin/env

If params are present in both SSM and external environment
then the latter will be used.
"""

import os
import sys
import argparse
import subprocess

import boto3

PROFILE_NAME = 'unitio'


def main(key_prefix, command, args, profile=None, region=None):
    """
    Run app with SSM params as environment.
    Return app exit code.
    """
    boto_kwargs = {}
    if profile is not None:
        boto_kwargs['profile_name'] = profile
    if region is not None:
        boto_kwargs['region_name'] = region
    session = boto3.Session(**boto_kwargs)
    ssm = session.client('ssm')

    parameters_iter = ssm.get_paginator('describe_parameters').paginate(
        Filters=[
            {
                'Key': 'Name',
                'Values': [key_prefix]
            }
        ],
        MaxResults=10
    )

    parameters = []
    for page in parameters_iter:
        parameters.extend(page['Parameters'])

    parameter_names = [parameter['Name'] for parameter in parameters]

    env = {}

    parameter_name_batch = []
    for i, parameter_name in enumerate(parameter_names):
        parameter_name_batch.append(parameter_name)
        if len(parameter_name_batch) == 10 or i == len(parameter_names) - 1:
            env.update({
                parameter['Name'].rpartition('/')[2]: parameter['Value']
                for parameter
                in ssm.get_parameters(
                    Names=parameter_name_batch,
                    WithDecryption=True
                )['Parameters']
            })
            parameter_name_batch = []

    sys.stderr.write('Retrieved {} parameters:\n'.format(len(env)))
    for key in env:
        sys.stderr.write('  - {}\n'.format(key))

    env.update(os.environ)
    proc = subprocess.Popen([command] + args, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr, env=env)
    proc.communicate()
    return proc.returncode


def entrypoint():
    """
    EnvAWS entrypoint.
    """
    parser = argparse.ArgumentParser(description='Run application with environment loaded from AWS SSM.')
    parser.add_argument('-p', '--profile', help='Override AWS config profile (omit to auto-detect.)')
    parser.add_argument('-r', '--region', help='Override region (omit to auto-detect)')
    parser.add_argument('-k', '--key-prefix', help='SSM key prefix', required=True)
    parser.add_argument('command', help='Child command to run.')
    parser.add_argument('args', nargs=argparse.REMAINDER, help='Child command arguments.', metavar='arg')
    sys.exit(main(**vars(parser.parse_args())))
