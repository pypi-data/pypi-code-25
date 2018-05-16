from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from makepy.shell import run, rm
import logging

log = logging.getLogger(__name__)

def tox(envlist=None):
    log.info('starting tox tests for envlist: %s', envlist)
    if envlist is None: run(['tox'])
    else:               run(['tox', '-e', envlist])

def clean(): rm('.tox')
