#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: plantain/consumer.py
# Author: Jimin Huang <huangjimin@whu.edu.cn>
# Date: 26.04.2018
import json
import kafka
import logging


LOGGER = logging.getLogger(__name__)


class Consumer(object):
    """Class for managing consumer context
    """
    def __init__(self, bootstrap_servers, topic, timeout, offset, group_id):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.timeout = int(timeout)
        self.offset = offset
        self.group_id = group_id

    def __enter__(self):
        LOGGER.info('Start consumer with {}'.format(self))

        try:
            timeout = int(self.timeout)
        except TypeError:
            timeout = float('inf')

        self.consumer = kafka.KafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            consumer_timeout_ms=timeout,
            auto_offset_reset=self.offset,
            group_id=self.group_id,
        )
        return self.consumer

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.consumer.close()
        if exc_tb is not None:
            LOGGER.info('Exit consumer with {0}: {1}'.format(
                exc_type, exc_value)
            )
            raise exc_value
        else:
            LOGGER.info('Exit consumer normal')

    def __str__(self):
        value_dict = dict(vars(self))
        del value_dict['bootstrap_servers']
        return json.dumps(value_dict)
