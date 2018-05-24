from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, Deferred, DeferredList
from twisted.internet.task import LoopingCall
from twisted.trial import unittest

from gtxamqp.factory import AmqpReconnectingFactory
from tests import utils


class TopicExchangeTests(unittest.TestCase):
    disconnecting_period = 2

    def setUp(self):
        self.fetched_counter = 0
        self.published_counter = 0
        self.total_messages_to_send = 200
        self.test_message = "test_message"
        self.tx = AmqpReconnectingFactory(**utils.generate_factory_config())
        self.client = self.tx.get_client(**utils.generate_client_config())

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
            print msg
            if msg.method.name != "get-empty":
                self.fetched_counter += 1
                self.assertEqual(msg.content.body, self.test_message)

            else:
                self.stop_the_show()
            print "GET", self.fetched_counter
            return msg

        def on_error(failure):
            print "Basic get failed: ", failure.getErrorMessage()

        ack_callback = lambda msg: msg
        if do_ack and not no_ack:
            ack_callback = lambda msg: self.client.basic_ack(msg)

        d = self.client.basic_get(no_ack=no_ack)
        d.addCallback(on_message).addCallback(ack_callback)
        d.addErrback(on_error)
        return d

    def consume_message(self, bulk_size, no_ack=True, do_ack=True, prefetch_counter=10):
        def on_message(msg):
            if msg:
                self.assertEqual(msg.content.body, self.test_message)
            if no_ack:
                self.fetched_counter += 1
                if self.fetched_counter == bulk_size:
                    self.stop_the_show()

            print "GET", self.fetched_counter, msg
            return msg

        def on_error(failure):
            print "Basic consume failed: ", failure.getErrorMessage()

        def ack_callback(msg):
            if do_ack and not no_ack:
                def increase_counter(*args):
                    self.fetched_counter += 1
                    if self.fetched_counter == bulk_size:
                        self.stop_the_show()
                d = self.client.basic_ack(msg.delivery_tag)
                d.addCallback(increase_counter)

        d = self.client.basic_consume(no_ack=no_ack, prefetch_count=prefetch_counter)
        d.addCallback(on_message).addCallback(ack_callback)
        d.addErrback(on_error)
        return d

    def publish_message(self):
        self.client.basic_publish(self.test_message, routing_key="#")
        print "PUT", self.published_counter
        if self.published_counter >= self.total_messages_to_send:
            self.publisher.stop()
        self.published_counter += 1
        return self.test_message

    @inlineCallbacks
    def test_01_pub_and_sub(self):
        yield self.tx.deferred
        self.show_stopper = Deferred()

        self.publisher = LoopingCall(self.publish_message)
        self.message_getter = LoopingCall(self.get_message)

        self.publisher.start(0.001)
        self.message_getter.start(0.001, False)
        yield self.show_stopper

    def disconnect(self):
        if self.client.p and self.client.p.connected:
            return p.transport.loseConnection()

    def tearDown(self):
        return self.tx.teardown()

    @inlineCallbacks
    def __wait(self, sec=5):
        d = Deferred()
        reactor.callLater(sec, d.callback, None)
        yield d

    @inlineCallbacks
    def publish_bulk(self, bulk_size=100):
        ds = []
        for i in xrange(bulk_size):
            ds.append(self.client.basic_publish(self.test_message))
        yield DeferredList(ds)
        yield self.__wait()
