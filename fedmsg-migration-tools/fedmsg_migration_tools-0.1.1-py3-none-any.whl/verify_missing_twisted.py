import json
import logging
from datetime import datetime, timedelta
from urllib.parse import urlparse

import pika
from pika.adapters import twisted_connection
from twisted.internet import defer, reactor, protocol, task
from twisted.python import log
from txzmq import (
    ZmqEndpoint, ZmqEndpointType, ZmqFactory, ZmqSubConnection,
)


_log = logging.getLogger(__name__)


class AmqpConsumer:

    def __init__(self, store, hostname=None, port=None, exchanges=None):
        self.store = store
        self.hostname = hostname or "localhost"
        self.port = port or 5672
        self.exchanges = exchanges or []
        self._connection = None
        self._running = False

    @defer.inlineCallbacks
    def run(self):
        parameters = pika.ConnectionParameters()
        cc = protocol.ClientCreator(
            reactor, twisted_connection.TwistedProtocolConnection, parameters)
        self._connection = yield cc.connectTCP(self.hostname, self.port)
        yield self._connection.ready
        channel = yield self._connection.channel()
        result = yield channel.queue_declare(
            auto_delete=True, exclusive=True)
        queue_name = result.method.queue
        for exchange_name in self.exchanges:
            yield channel.exchange_declare(
                exchange=exchange_name, exchange_type="topic", durable=True)
            yield channel.queue_bind(
                exchange=exchange_name, queue=queue_name, routing_key='#')
        yield channel.basic_qos(prefetch_count=1)
        queue_object, consumer_tag = yield channel.basic_consume(
            queue=queue_name, no_ack=False)
        self._running = True
        reactor.callLater(0.1, self.read, queue_object)
        #self._read_task = task.LoopingCall(self._read, queue_object)
        #self._read_task.start(0.01)

    @defer.inlineCallbacks
    def read(self, queue_object):
        _log.info('AMQP consumer is ready')
        while self._running:
            ch, method, properties, body = yield queue_object.get()
            if body:
                self.on_message(ch, method, properties, body)
            yield ch.basic_ack(delivery_tag=method.delivery_tag)

    @defer.inlineCallbacks
    def stop(self):
        if not self._running:
            return
        self._running = False
        print(self._connection.close())

    def on_message(self, ch, method, properties, body):
        topic = method.routing_key
        _log.debug('Received message on "%s"', topic)
        try:
            msg = json.loads(body)
        except ValueError as e:
            _log.warning("Invalid message: %r", body)
            return
        _log.debug('Received from AMQP on topic %s: %s', topic, msg["msg_id"])
        self.store[msg["msg_id"]] = (
            datetime.utcnow(),
            msg,
        )


class ZmqConsumer:

    def __init__(self, store, endpoints, topics):
        self.store = store
        self.endpoints = endpoints
        self.topics = topics
        self._socket = None
        self._factory = None

    def run(self):
        self._factory = ZmqFactory()
        endpoints = [
            ZmqEndpoint(ZmqEndpointType.connect, endpoint)
            for endpoint in self.endpoints
        ]
        for topic in self.topics:
            _log.debug('Configuring ZeroMQ subscription socket with the "%s" topic', topic)
            for endpoint in endpoints:
                s = ZmqSubConnection(self._factory, endpoint)
                s.subscribe(topic.encode('utf-8'))
                s.gotMessage = self.on_message
        _log.info('ZeroMQ consumer is ready')

    def on_message(self, body, topic):
        topic = topic.decode("utf-8")
        msg = json.loads(body)
        _log.debug('Received from ZeroMQ on topic %s: %s',
                   topic, msg["msg_id"])
        self.store[msg["msg_id"]] = (
            datetime.utcnow(),
            msg,
        )

    def stop(self):
        self._factory.shutdown()


class Comparator:

    MATCH_WINDOW = 20

    def __init__(self, amqp_store, zmq_store):
        self.amqp_store = amqp_store
        self.zmq_store = zmq_store
        self._rm_loop = task.LoopingCall(self.remove_matching)
        self._cm_loop = task.LoopingCall(self.check_missing)

    def run(self):
        self._rm_loop.start(1)
        self._cm_loop.start(10)

    def remove_matching(self):
        _log.debug("Checking for matching messages (%i, %i)",
                   len(self.amqp_store), len(self.zmq_store))
        for msg_id in list(self.amqp_store.keys()):
            if msg_id in self.zmq_store:
                del self.amqp_store[msg_id]
                del self.zmq_store[msg_id]

    def check_missing(self):
        _log.debug("Checking for missing messages")
        self._check_store(self.amqp_store, "AMQP")
        self._check_store(self.zmq_store, "ZeroMQ")

    def _check_store(self, store, source_name):
        threshold = datetime.utcnow() - timedelta(seconds=self.MATCH_WINDOW)
        for msg_id, value in list(store.items()):
            time, msg = value
            if time < threshold:
                _log.warning("Message %s was only received in %s",
                             msg_id, source_name)
                del store[msg_id]


def main(amqp_url, zmq_endpoints, exchanges):
    amqp_store = {}
    zmq_store = {}
    comparator = Comparator(amqp_store, zmq_store)
    comparator.run()
    zmq_consumer = ZmqConsumer(
        zmq_store, zmq_endpoints, [""])
    zmq_consumer.run()
    amqp_url = urlparse(amqp_url)
    amqp_consumer = AmqpConsumer(
        amqp_store, amqp_url.hostname, amqp_url.port, exchanges)
    d = amqp_consumer.run()
    d.addErrback(log.err)
    try:
        reactor.run()
    except KeyboardInterrupt:
        d = defer.DeferredList([
            amqp_consumer.stop(),
            zmq_consumer.stop(),
        ])
        d.addCallback(lambda _: reactor.stop())
        reactor.run()
