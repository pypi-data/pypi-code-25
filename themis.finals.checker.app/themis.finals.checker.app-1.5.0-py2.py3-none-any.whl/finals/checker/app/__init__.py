# -*- coding: utf-8 -*-
from __future__ import absolute_import
from rq import Connection, Worker
from redis import Redis
import os
import os.path
import logging.config
import io
import yaml


logging_config_file = os.getenv('LOGGING_CONFIG_FILE', '')
if os.path.exists(logging_config_file):
    with io.open(logging_config_file, 'rb') as f:
        logging.config.dictConfig(yaml.load(f, yaml.Loader))


def start_worker():
    from . import worker
    redis_host = os.getenv('REDIS_HOST', '127.0.0.1')
    redis_port = int(os.getenv('REDIS_PORT', '6379'))
    redis_db = int(os.getenv('REDIS_DB', '0'))
    redis_password = os.getenv('REDIS_PASSWORD', None)

    with Connection(Redis(host=redis_host, port=redis_port, db=redis_db,
                          password=redis_password)):
        Worker(['default']).work()
