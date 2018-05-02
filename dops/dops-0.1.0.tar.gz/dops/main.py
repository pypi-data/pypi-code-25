#!/usr/bin/env python3
# coding=utf-8

"""
@version: 0.1
@author: ysicing
@file: dops/main.py 
@time: Apr 27, 14:16
"""

from dops.core import Dops

import logging
logger = logging.getLogger(__name__)


def cli():
    dops_cli = Dops()
    logger.info("session start")
    dops_cli.run_cli()

if __name__ == "__main__":
    cli()