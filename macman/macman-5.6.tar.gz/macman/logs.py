#!/usr/bin/python
# Filename: logs.py

import logging
from logging.handlers import RotatingFileHandler
import os
import __builtin__
import macman


log_path = '/usr/local/techops/logs/'


def setupLogging(log_file=None):
    """  Setup logging parameters """

    # if no log file name provided, don't setup logging
    if log_file is None:
        __builtin__.log = None

    # if log file name provided, setup logging
    else:

        # set directory path for log storage
        if not os.path.exists(log_path):
            os.makedirs(log_path)

        # set file permissions so non-root users can write to logs
        macman.files.setPathPermissions(log_path, '0777')

        # setup log rotation
        handler = RotatingFileHandler('%s%s' % (log_path, log_file), mode='a', maxBytes=5 * 1024 * 1024, backupCount=1,
                                      encoding=None, delay=0)

        # set log format
        log_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(log_formatter)

        handler.setLevel(logging.INFO)

        log = logging.getLogger('root')
        log.setLevel(logging.INFO)
        log.addHandler(handler)

        # pass log to __builtin__ so it will be accessible across the module
        __builtin__.log = log


def writeLog(log_string=None):
    """ If log not True don't log. If log_string contains \\n, insert \\t before for formatting """

    if log and log_string:
        log_string = '\t'.join(log_string.strip().splitlines(True))
        log.info(log_string)

