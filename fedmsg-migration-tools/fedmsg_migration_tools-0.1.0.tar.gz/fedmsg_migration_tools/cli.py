"""
The ``fedmsg-migration-tools`` `Click`_ CLI.

.. _Click: http://click.pocoo.org/
"""
from __future__ import absolute_import

import logging
import logging.config

import click
import zmq

from . import config, bridges as bridges_module

_log = logging.getLogger(__name__)


@click.group()
@click.option('--conf', envvar='FEDMSG_MIGRATION_TOOLS_CONFIG')
def cli(conf):
    """
    The fedmsg-migration-tools command line interface.

    This can be used to run AMQP <-> ZMQ bridge services.
    """
    if conf:
        try:
            config.conf.load_config(filename=conf)
        except ValueError as e:
            raise click.exceptions.BadParameter(e)


@cli.command()
@click.option('--topic', multiple=True)
@click.option('--zmq-endpoint', multiple=True, help='A ZMQ socket to subscribe to')
@click.option('--exchange')
@click.option('--amqp-url')
def zmq_to_amqp(amqp_url, exchange, zmq_endpoint, topic):
    """Bridge ZeroMQ messages to an AMQP exchange."""
    amqp_url = amqp_url or config.conf['amqp_url']
    topics = topic or config.conf['zmq_to_amqp']['topics']
    exchange = exchange or config.conf['zmq_to_amqp']['exchange']
    zmq_endpoints = zmq_endpoint or config.conf['zmq_to_amqp']['zmq_endpoints']
    topics = [t.encode('utf-8') for t in topics]
    try:
        bridges_module.zmq_to_amqp(amqp_url, exchange, zmq_endpoints, topics)
    except Exception:
        _log.exception('An unexpected error occurred, please file a bug report')


@cli.command()
@click.option('--publish-endpoint')
@click.option('--bindings')
@click.option('--queue-name')
@click.option('--amqp-url')
def amqp_to_zmq(amqp_url, queue_name, bindings, publish_endpoint):
    """Bridge an AMQP queue to a ZeroMQ PUB socket."""
    amqp_url = amqp_url or config.conf['amqp_url']
    queue_name = queue_name or config.conf['amqp_to_zmq']['queue_name']
    bindings = bindings or config.conf['amqp_to_zmq']['bindings']
    publish_endpoint = publish_endpoint or config.conf['amqp_to_zmq']['publish_endpoint']
    try:
        bridges_module.amqp_to_zmq(amqp_url, queue_name, bindings, publish_endpoint)
    except zmq.error.ZMQError as e:
        _log.error(str(e))
    except Exception:
        _log.exception('An unexpected error occurred, please file a bug report')
