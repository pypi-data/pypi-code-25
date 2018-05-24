# -*- coding: utf-8 -*-

import pika
import json
from ..base_consumer import CocoBaseConsumer

class CocoRMQConsumer(CocoBaseConsumer):

    def __init__(self, conf, worker, logger = None):
        self._exchange_name = conf['EXCHANGE_NAME']
        self._queue_name = conf['QUEUE_NAME']
        self._exchange_type = conf['EXCHANGE_TYPE']
        self._connection = None
        super().__init__(conf, worker, logger)

    def connect(self):
        credentials = pika.PlainCredentials(self._config['USERNAME'], self._config['PASSWORD'])
        parameters = pika.ConnectionParameters(self._config['SERVER_ADDRESS'],
                                               self._config['SERVER_PORT'],
                                               '/',
                                               credentials)

        self._connection = pika.BlockingConnection(parameters)

        channel = self._connection.channel()
        channel.exchange_declare(exchange = self._exchange_name,
                                 exchange_type = self._exchange_type)

        result = channel.queue_declare(queue = self._queue_name, durable=True)
        name = result.method.queue
        channel.queue_bind(exchange = self._exchange_name,
                           queue = result.method.queue)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.on_message,
                              queue=self._queue_name)

        channel.start_consuming()

    def on_message(self, ch, method, properties, body):
        self._worker.process(body)
        ch.basic_ack(delivery_tag = method.delivery_tag)