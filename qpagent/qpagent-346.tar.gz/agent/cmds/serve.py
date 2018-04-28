#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import signal

import click

import agent
from agent.api.qualityplatform import QualityPlatform
from agent.exc import GracefulExitException
from agent.server.api import start_server, stop_server

logger = logging.getLogger(__name__)

if "AGENT_ENV" in os.environ:
    qualityplatform_client = QualityPlatform(os.environ["AGENT_ENV"])
else:
    qualityplatform_client = QualityPlatform('alpha')


def output_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo("Agent Server Version:")
    click.echo("Version: {}".format(agent.__version__))
    ctx.exit()


@click.command()
@click.option(
    '-v',
    '--version',
    is_flag=True,
    is_eager=True,
    callback=output_version,
    expose_value=False,
    help="show the version of this tool")
@click.option(
    '-l',
    '--log',
    default='INFO',
    help='Specify logging level, default is INFO')
def serve(log):
    log_level = getattr(logging, log.upper())
    logging.basicConfig(level=log_level)
    start_agent_client()


def signal_handler(signum, frame):
    stop_server()
    logger.info("main process(%d) got GracefulExitException" % os.getpid())
    os._exit(0)


def start_agent_client():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    try:
        start_server()
    except GracefulExitException as e:
        logger.error(e.message, exe_info=True)
