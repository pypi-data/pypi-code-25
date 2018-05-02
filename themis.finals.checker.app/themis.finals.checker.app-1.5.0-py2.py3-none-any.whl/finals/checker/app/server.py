# -*- coding: utf-8 -*-
from __future__ import absolute_import
import flask
import redis
import rq
import os
import logging
from .worker import queue_push, queue_pull

logger = logging.getLogger(__name__)

queue = rq.Queue(connection=redis.Redis(
    host=os.getenv('REDIS_HOST', '127.0.0.1'),
    port=int(os.getenv('REDIS_PORT', '6379')),
    db=int(os.getenv('REDIS_DB', '0')),
    password=os.getenv('REDIS_PASSWORD', None)
))

app = flask.Flask(__name__)
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False

default_push_run_timeout = int(
    os.getenv('THEMIS_FINALS_CHECKER_PUSH_RUN_TIMEOUT', '60')
)
default_push_queue_ttl = int(
    os.getenv('THEMIS_FINALS_CHECKER_PUSH_QUEUE_TTL', '60')
)
default_pull_run_timeout = int(
    os.getenv('THEMIS_FINALS_CHECKER_PULL_RUN_TIMEOUT', '30')
)
default_pull_queue_ttl = int(
    os.getenv('THEMIS_FINALS_CHECKER_PULL_QUEUE_TTL', '30')
)
default_result_ttl = int(os.getenv('THEMIS_FINALS_CHECKER_RESULT_TTL', '60'))


@app.teardown_request
def teardown_request(exception=None):
    if exception:
        logger.error('Uncaught exception!', exc_info=exception)


@app.route('/push', methods=['POST'])
def push():
    payload = flask.request.get_json()
    if payload is None:
        return '', 400
    queue.enqueue_call(
        func=queue_push,
        args=(payload,),
        timeout=default_push_run_timeout,
        ttl=default_push_queue_ttl,
        result_ttl=default_result_ttl
    )
    return '', 202


@app.route('/pull', methods=['POST'])
def pull():
    payload = flask.request.get_json()
    if payload is None:
        return '', 400
    queue.enqueue_call(
        func=queue_pull,
        args=(payload,),
        timeout=default_pull_run_timeout,
        ttl=default_pull_queue_ttl,
        result_ttl=default_result_ttl
    )
    return '', 202
