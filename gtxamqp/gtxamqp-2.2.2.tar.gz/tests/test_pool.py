import random

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, Deferred
from twisted.internet.task import LoopingCall
from twisted.trial import unittest

from gtxamqp.factory import MAX_CHANNELS_PER_CONNECTION
from gtxamqp.pool import pool
from tests import utils


class ConnectionPoolTests(unittest.TestCase):
    disconnecting_period = 2
    timeout = 200

    def setUp(self):
        self.fetched_counter = 1
        self.published_counter = 0
        self.total_messages_to_send = 1000
        self.clients = [pool.get(rabbitmq_conf=utils.generate_rabbitmq_config()) for _ in xrange(5)]
        self.client_by_message = {}

    def factory_by_message(self, msg):
        return self.client_by_message[msg]

    def stop_the_show(self):
        if hasattr(self, "disconnector"):
            self.disconnector.stop()
        if hasattr(self, "message_getter") and self.message_getter.running:
            self.message_getter.stop()
        if hasattr(self, "publisher") and self.publisher.running:
            self.publisher.stop()
        if self.show_stopper:
            reactor.callLater(self.disconnecting_period, self.show_stopper.callback, None)
            self.show_stopper = None

    def get_message(self, no_ack=True, do_ack=True):
        def on_message(msg):
            if msg.method.name != "get-empty":
                self.fetched_counter += 1

            elif self.fetched_counter >= self.total_messages_to_send:
                self.stop_the_show()
            return msg

        def on_error(failure):
            print "Basic get failed: ", failure.getErrorMessage()

        ack_callback = lambda msg: msg
        if do_ack and not no_ack:
            def ack_callback(msg):
                client = self.client_by_message[hash(msg)]
                client.basic_ack(msg) if msg.content else None

            ack_callback = ack_callback

        client = random.choice(self.clients)
        d = client.basic_get(no_ack=no_ack)
        d.addCallback(on_message).addCallback(ack_callback)
        d.addErrback(on_error)
        return d

    def publish_message(self):
        client = random.choice(self.clients)
        msg = utils.generate_message()
        self.client_by_message[hash(msg)] = client

        client.basic_publish(msg, None)
        self.published_counter += 1
        if self.published_counter >= self.total_messages_to_send:
            self.publisher.stop()
        return msg

    def tearDown(self):
        return pool.teardown()

    @inlineCallbacks
    def test_01_pub_and_sub(self):
        self.show_stopper = Deferred()
        self.publisher = LoopingCall(self.publish_message)
        self.message_getter = LoopingCall(self.get_message)
        self.publisher.start(0)
        self.message_getter.start(0, False)
        yield self.show_stopper

    @inlineCallbacks
    def test_02_pool_overflow_creates_new_connection(self):
        # there should be one factory at the beginning
        self.assertEqual(len(pool), 1, "")
        for n in xrange(MAX_CHANNELS_PER_CONNECTION - len(self.clients) + 1):
            self.clients.append(pool.get(rabbitmq_conf=utils.generate_rabbitmq_config()))

        # all the channels for the factory have been used,
        # a new factory should be added now
        self.assertEqual(len(pool), 2, "")

        # remove all the clients
        for tx in list(pool):
            for client in tx.clients.values():
                yield client.teardown()

        for _ in xrange(MAX_CHANNELS_PER_CONNECTION):
            self.clients.append(pool.get(rabbitmq_conf=utils.generate_rabbitmq_config()))

        self.assertEqual(len(pool), 2, "")
