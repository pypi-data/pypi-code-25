#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import argparse
import logging
import os
from time import sleep, time

from pkg_resources import Requirement, resource_string

from . import conf
from . import glb
from . import version
from .performer import Performer
from .utils.strhelper import to_str

_parser = None  # type: argparse.ArgumentParser


def set_get_arguments():  # type:()->argparse.Namespace
    global _parser
    _parser = argparse.ArgumentParser(
        prog=version.NAME,
        description='Watch files in a directory and upload them to Aliyun OSS on file writing completed')
    _parser.add_argument(
        '--version', action='version',
        version='%(prog)s {0}'.format(version.__version__)
    )

    subparsers = _parser.add_subparsers(
        dest='sub_command',
        description='',
        help='<sub-command --help> Print the help of sub-commands'
    )

    parser_run = subparsers.add_parser(
        'run',
        help='Start to run then program. It will monitor and upload files continuously.')
    parser_run.add_argument(
        '--config-file', '-c', type=str, default='',
        help='The program configuration file')
    parser_run.add_argument(
        '--logging-config-file', '-l', type=str, default='',
        help='The logging configuration file')

    parser_echo_config_sample = subparsers.add_parser(
        'echo_config_sample',
        help='Echo configure file sample')
    parser_echo_config_sample.add_argument(
        'config', type=str, choices=['prog', 'log'],
        help='Configure file to echo')

    arguments = _parser.parse_args()
    return arguments


def main():
    arguments = set_get_arguments()

    if arguments.sub_command == 'echo_config_sample':
        paths = version.NAMESPACE.split('.')
        paths.extend([
            'data',
            'config-samples',
            '{0}.yaml'.format(arguments.config)
        ])
        resource_name = os.path.join(*paths)
        txt = resource_string(Requirement.parse(version.NAME), resource_name)
        print('{0}{1}{0}'.format(os.linesep, to_str(txt)))

    elif arguments.sub_command == 'run':
        conf.load_logging_config()
        logger = get_logger()

        conf.load_program_config()

        logger.info('-' * 60)
        logger.info('Starting')
        logger.info('configuration: %s', glb.config)
        logger.info('-' * 60)
        try:
            interval = float(glb.config['watcher']['interval'])
            Performer.initial()
            while True:
                ts = time()
                Performer.run_once()
                sleep_secs = interval - (time() - ts)
                if sleep_secs > 0:
                    sleep(sleep_secs)
        except KeyboardInterrupt:
            logger.warning('SIGINT')
        except Exception:
            logger.exception('')
            raise
        finally:
            Performer.release()
            logger.info('=' * 60)
            logger.info('Stopped')
            logger.info('=' * 60)

    else:
        _parser.print_help()


def get_logger():
    return logging.getLogger(version.NAMESPACE)


if __name__ == '__main__':
    main()
