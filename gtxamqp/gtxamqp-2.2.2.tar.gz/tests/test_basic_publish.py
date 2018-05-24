from twisted.internet.defer import inlineCallbacks
from twisted.trial import unittest
from txamqp.client import ChannelClosed

from gtxamqp.factory import AmqpReconnectingFactory
from tests import utils


class BasicPublishTests(unittest.TestCase):

    def setUp(self):
        self.tx = AmqpReconnectingFactory(**utils.generate_factory_config())
        self.client = self.tx.get_client(**utils.generate_client_config())

    @inlineCallbacks
    def test_basic_publish(self):
        # mock the retry function and wait for it to get called
        # it should get called only if an exception was raised
        try:
            yield self.client.basic_publish("random-message",
                                            exchange="unknown-exchange")
        except:
            self.fail("published to a non-existing exchange without confirmation, and an exception was raised")


    def tearDown(self):
        return self.tx.teardown()
