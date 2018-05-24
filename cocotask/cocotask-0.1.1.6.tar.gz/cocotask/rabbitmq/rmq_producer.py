# -*- coding: utf-8 -*-

import redis
import json
import pika
from ..base_producer import CocoBaseProducer

class CocoRMQProducer(CocoBaseProducer):

    def __init__(self, conf, logger = None):
        self._exchange_name = conf['EXCHANGE_NAME']
        self._queue_name = conf['QUEUE_NAME']
        self._exchange_type = conf['EXCHANGE_TYPE']
        self._connection = None
        self._channel = None
        super().__init__(conf, logger)

    def connect(self):
        credentials = pika.PlainCredentials(self._config['USERNAME'], self._config['PASSWORD'])
        parameters = pika.ConnectionParameters(self._config['SERVER_ADDRESS'],
                                               self._config['SERVER_PORT'],
                                               '/',
                                               credentials)
        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()

        self._channel.exchange_declare(exchange=self._exchange_name,
                                 exchange_type=self._exchange_type)
        self._channel.queue_declare(queue=self._queue_name, durable=True)


    def send(self, data):
      self._channel.basic_publish(exchange=self._exchange_name, 
                      routing_key=self._queue_name, 
                      body=data, 
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))

    def close(self):
        self._connection.close()


