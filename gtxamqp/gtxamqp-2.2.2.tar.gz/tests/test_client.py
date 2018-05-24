import time
from collections import defaultdict

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, Deferred, DeferredList, returnValue
from twisted.internet.task import LoopingCall
from twisted.trial import unittest

from gtxamqp.factory import AmqpReconnectingFactory
from tests import utils


class ClientTests(unittest.TestCase):
    disconnecting_period = 2
    timeout = 180

    def setUp(self):
        self.disconnects_counter = 0
        self.fetched_counter = 1
        self.published_counter = 0
        self.total_messages_to_send = 1000
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
            reactor.callLater(self.disconnecting_period,
                              self.show_stopper.callback,
                              None)

            self.show_stopper = None

    def get_disconnector(self, items_processed_func, num=750):
        class ItemsProcessed(object):
            def __init__(self):
                self.items_processed = 0

        processor = ItemsProcessed()

        # this is needed to ensure we don't disconnect
        # if a small amount of items were processed
        # because it would cause the test to run really slow
        # if the reactor decided to fire consequent disconnects
        def disconnect_after_processed_at_least_x_items():
            last_processed = processor.items_processed
            processor.items_processed = items_processed_func()
            return processor.items_processed - last_processed > num

        return LoopingCall(self.disconnect,
                           disconnect_after_processed_at_least_x_items)

    def get_message(self, no_ack=True, do_ack=True):
        def on_message(msg):
            # print msg
            if msg.method.name != "get-empty":
                self.fetched_counter += 1
                if self.fetched_counter % 100 == 0:
                    print("messages fetched %d messages" % self.fetched_counter)

                self.assertEqual(msg.content.body, self.test_message)
            else:
                self.stop_the_show()

            return msg

        def on_error(failure):
            print "Basic get failed: ", failure.getErrorMessage()

        ack_callback = lambda msg: msg

        if do_ack and not no_ack:
            ack_callback = lambda msg: self.client.basic_ack(msg.delivery_tag) if msg.content else None

        d = self.client.basic_get(no_ack=no_ack)
        d.addCallback(on_message).addCallback(ack_callback)
        d.addErrback(on_error)
        return d

    def publish_message(self):
        self.client.basic_publish(self.test_message)
        # print "PUT", self.published_counter
        self.published_counter += 1
        if self.published_counter >= self.total_messages_to_send:
            self.publisher.stop()

        return self.test_message

    def disconnect(self, should_disconnect=None):
        if should_disconnect and \
           hasattr(should_disconnect, "__call__") \
           and not should_disconnect():
            return

        if self.client.p and self.client.p.connected:
            self.disconnects_counter += 1
            return self.client.p.transport.loseConnection()

    def tearDown(self):
        return self.tx.teardown()

    @inlineCallbacks
    def __wait(self, sec=5):
        d = Deferred()
        reactor.callLater(sec, d.callback, None)
        yield d

    @inlineCallbacks
    def publish_bulk(self):
        ds = []
        for i in xrange(self.bulk_size):
            ds.append(self.client.basic_publish(self.test_message))

        yield DeferredList(ds)
        yield self.__wait()

    @inlineCallbacks
    def on_message(self, msg):
        self.assertEqual(msg.content.body, self.test_message)
        if self.fetched_counter == self.bulk_size:
            self.stop_the_show()

        if not msg.__dict__.get("no_ack"):
            yield self.client.basic_ack(msg.delivery_tag)

        self.fetched_counter += 1
        if self.fetched_counter % 100 == 0:
            print("messages fetched %d messages" % self.fetched_counter)

        returnValue(msg)

    @inlineCallbacks
    def test_00_pub_and_sub(self):
        yield self.tx.deferred
        self.show_stopper = Deferred()
        self.publisher = LoopingCall(self.publish_message)
        self.message_getter = LoopingCall(self.get_message)
        self.publisher.start(0)
        self.message_getter.start(0, False)
        yield self.show_stopper


    @inlineCallbacks
    def test_01_pub_and_sub(self):
        yield self.tx.deferred
        self.show_stopper = Deferred()
        self.publisher = LoopingCall(self.publish_message)
        self.message_getter = LoopingCall(self.get_message)
        self.publisher.start(0)
        self.message_getter.start(0, False)
        yield self.show_stopper

    @inlineCallbacks
    def test_02_pub_and_sub_on_disconnect(self):
        yield self.tx.deferred
        self.show_stopper = Deferred()
        self.total_messages_to_send = 5000
        self.publisher = LoopingCall(self.publish_message)
        self.message_getter = LoopingCall(self.get_message)
        items_processed_func = lambda: self.fetched_counter
        self.disconnector = self.get_disconnector(items_processed_func)
        self.disconnector.start(self.disconnecting_period)
        self.publisher.start(0)
        self.message_getter.start(0, False)
        yield self.show_stopper


    @inlineCallbacks
    def test_03_pub_and_sub_and_ack(self):
        yield self.tx.deferred
        self.show_stopper = Deferred()
        self.publisher = LoopingCall(self.publish_message)
        self.message_getter = LoopingCall(self.get_message, no_ack=False)
        self.publisher.start(0)
        self.message_getter.start(0)
        yield self.show_stopper

    @inlineCallbacks
    def test_04_pub_and_sub_and_ack_on_disconnect(self):
        yield self.tx.deferred
        self.show_stopper = Deferred()
        self.publisher = LoopingCall(self.publish_message)
        self.message_getter = LoopingCall(self.get_message, no_ack=False)
        items_processed_func = lambda: self.fetched_counter
        self.disconnector = self.get_disconnector(items_processed_func)
        self.disconnector.start(self.disconnecting_period)
        self.publisher.start(0)
        self.message_getter.start(0, False)
        yield self.show_stopper

    @inlineCallbacks
    def test_05_stop_retry_stops_the_reconnecting_factory(self):
        yield self.tx.deferred
        self.total_messages_to_send = 1000000000
        self.show_stopper = Deferred()
        self.publisher = LoopingCall(self.publish_message)
        self.message_getter = LoopingCall(self.get_message, no_ack=False)
        items_processed_func = lambda: self.fetched_counter
        self.disconnector = self.get_disconnector(items_processed_func)
        self.disconnector.start(self.disconnecting_period)
        self.publisher.start(0)
        self.message_getter.start(0, False)

        reactor.callLater(2, self.tx.stopTrying)
        reactor.callLater(4, self.stop_the_show)
        yield self.show_stopper

        self.assertTrue(self.tx.continueTrying == 0, "client keeps trying even though it was stopped")
        self.assertLess(self.published_counter, self.total_messages_to_send)
        self.assertLess(self.fetched_counter, self.total_messages_to_send)

    @inlineCallbacks
    def test_06_basic_recover(self):
        yield self.tx.deferred
        self.show_stopper = Deferred()
        self.publisher = LoopingCall(self.publish_message)
        self.message_getter = LoopingCall(self.get_message,
                                          no_ack=False,
                                          do_ack=False)
        self.publisher.start(0)
        self.message_getter.start(0, False)
        yield self.show_stopper
        msg = yield self.client.basic_get()
        self.assertEqual(msg.method.name, "get-empty")
        yield self.client.basic_recover()
        msg = yield self.client.basic_get()
        self.assertNotEqual(msg.method.name, "get-empty")


    @inlineCallbacks
    def test_07_delete_queue(self):
        yield self.tx.deferred
        yield self.client.queue_declare()
        yield self.client.queue_delete()

        try:
            yield self.client.queue_declare(passive=True, **self.client.queue)
            exception_thrown = False
        except:
            exception_thrown = True

        self.assertTrue(exception_thrown)

    @inlineCallbacks
    def test_08_delete_exchange(self):
        yield self.tx.deferred
        # random channel needs an channels to exist
        yield self.client.deferred
        yield self.client.p.get_random_channel().exchange_declare(**self.client.exchange)
        yield self.client.exchange_delete()

        try:
            yield self.client.p.random_channel.exchange_declare(passive=True, **self.client.exchange)
            exception_thrown = False
        except:
            exception_thrown = True

        self.assertTrue(exception_thrown)

    @inlineCallbacks
    def test_09_basic_consume_with_noack(self):
        self.bulk_size = 1000
        yield self.tx.deferred
        yield self.publish_bulk()
        st = time.time()
        self.show_stopper = Deferred()
        ctag = yield self.client.basic_consume(callback=self.on_message, no_ack=True)
        yield self.show_stopper
        yield self.client.basic_cancel(consumer_tag=ctag)
        print "Consumer with no_ack=True", self.bulk_size / (time.time() - st), "msg/s"

    @inlineCallbacks
    def test_10_basic_consume_with_ack(self):
        yield self.tx.deferred
        self.bulk_size = 1000
        self.total_messages_to_send = self.bulk_size
        self.publisher = LoopingCall(self.publish_message)
        self.publisher.start(0)

        st = time.time()
        self.show_stopper = Deferred()

        ctag = yield self.client.basic_consume(callback=self.on_message)
        yield self.show_stopper
        yield self.client.basic_cancel(consumer_tag=ctag)
        print "Consumer with no_ack=False", self.bulk_size / (time.time() - st), "msg/s"

    @inlineCallbacks
    def test_11_basic_consume_qos_with_ack_with_disconnect(self):
        yield self.tx.deferred
        self.bulk_size = 5000
        yield self.publish_bulk()
        yield self.__wait()
        items_processed_func = lambda: self.fetched_counter
        self.disconnector = self.get_disconnector(items_processed_func)
        self.disconnector.start(self.disconnecting_period, False)
        st = time.time()
        self.show_stopper = Deferred()
        ctag = yield self.client.basic_consume(callback=self.on_message)
        yield self.show_stopper
        yield self.client.basic_cancel(consumer_tag=ctag)
        print "Consumer with no_ack=False", self.bulk_size / (time.time() - st), "msg/s"

    @inlineCallbacks
    def test_12_basic_consume_with_ack_multiply_consumers(self):
        yield self.tx.deferred
        self.bulk_size = 5000
        self.total_messages_to_send = self.bulk_size
        self.publisher = LoopingCall(self.publish_message)
        self.publisher.start(0)
        yield self.__wait()

        st = time.time()
        self.show_stopper = Deferred()
        msgs_per_consumer = defaultdict(int)

        @inlineCallbacks
        def on_message_determine_consumer(msg):
            msg = yield self.on_message(msg)
            msgs_per_consumer[msg.consumer_tag] += 1

        ctags = []
        for i in xrange(10):
            ctag = yield self.client.basic_consume(callback=on_message_determine_consumer)
            ctags.append(ctag)

        yield self.show_stopper
        for ctag in ctags:
            yield self.client.basic_cancel(ctag)

        messages_received = msgs_per_consumer.values()
        self.assertEqual(len(self.client._consumers), 0)
        self.assertTrue(all(messages_received))
        self.assertGreaterEqual(sum(messages_received), self.bulk_size)

        self.assertEqual(self.bulk_size, sum(msgs_per_consumer.values()))
        print "Consumer with no_ack=True", self.bulk_size / (time.time() - st), "msg/s"
        print "Duplicates rate: %s %%" % ((float(sum(messages_received) - self.bulk_size) / self.bulk_size) * 100)

    @inlineCallbacks
    def test_13_basic_consume_with_ack_multiply_consumers_with_disconnect(self):
        yield self.tx.deferred
        self.bulk_size = 5000
        self.total_messages_to_send = self.bulk_size
        self.publisher = LoopingCall(self.publish_message)
        self.publisher.start(0)
        yield self.__wait(10)

        items_processed_func = lambda: sum(msgs_per_consumer.values())
        self.disconnector = self.get_disconnector(items_processed_func)
        self.disconnector.start(self.disconnecting_period, False)
        st = time.time()
        self.show_stopper = Deferred()
        msgs_per_consumer = defaultdict(int)

        @inlineCallbacks
        def on_message_determine_consumer(msg):
            msg = yield self.on_message(msg)
            msgs_per_consumer[msg.consumer_tag] += 1

        ctags = []
        for i in xrange(3):
            ctag = yield self.client.basic_consume(callback=on_message_determine_consumer)
            ctags.append(ctag)

        yield self.show_stopper
        for ctag in ctags:
            yield self.client.basic_cancel(consumer_tag=ctag)

        messages_received = msgs_per_consumer.values()
        self.assertEqual(len(self.tx._consumers), 0)
        self.assertTrue(all(messages_received))
        self.assertGreaterEqual(sum(messages_received), self.bulk_size)
        print "Consumer with no_ack=True", self.bulk_size / (time.time() - st), "msg/s"
        print "Disconnected %s times every %s sec, Duplicates rate: %s %%" % (
            self.disconnects_counter, self.disconnecting_period,
            (float(sum(messages_received) - self.bulk_size) / self.bulk_size) * 100)
