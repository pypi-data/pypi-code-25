import random

import mock
import txamqp.client
from twisted.internet.defer import inlineCallbacks, Deferred
from twisted.internet.task import LoopingCall
from twisted.trial import unittest

from gtxamqp.factory import AmqpReconnectingFactory
from tests import utils


class ChannelClosedTests(unittest.TestCase):
    disconnecting_period = 2

    def setUp(self):
        self.fetched_counter = 0
        self.published_counter = 0
        self.total_messages_to_send = 500

        self.tx = AmqpReconnectingFactory(**utils.generate_factory_config())
        self.client = self.tx.get_client(**utils.generate_client_config())

        self.exception_raised = Deferred()
        self.consumer = LoopingCall(self.get_message_callback_on_exception, d=self.exception_raised)
        self.consumer.start(0.01)

    @inlineCallbacks
    def get_message_callback_on_exception(self, d):
        try:
            yield self.client.basic_get()
        except Exception as e:
            if not d.called:
                d.callback(e)

    @inlineCallbacks
    def test_reconnect_on_channel_closed(self):
        # mock the retry function and wait for it to get called
        # it should get called only if an exception was raised
        self.tx.retry = mock.MagicMock()
        reconnection_occurred = Deferred()

        def retry_called(*x):
            AmqpReconnectingFactory.retry(self.tx)
            if self.exception_raised.called:
                reconnection_occurred.callback(None)

        self.tx.retry.side_effect = retry_called
        # when ack'ing a message that doesn't exist
        yield self.client.basic_ack(random.randint(2, 50))
        exc = yield self.exception_raised
        fmt= "expected exception {} to be raised, got: {}"
        self.assertIs(type(exc), txamqp.client.ChannelClosed,
                      fmt.format(txamqp.client.ChannelClosed, type(exc)))
        yield reconnection_occurred

    @inlineCallbacks
    def tearDown(self):
        yield self.tx.teardown()
        stopper = self.consumer.deferred
        self.consumer.stop()
        yield stopper
