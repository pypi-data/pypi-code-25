from twisted.internet.defer import inlineCallbacks
from twisted.trial import unittest

from gtxamqp.factory import AmqpReconnectingFactory
from tests import utils


class TeardownTests(unittest.TestCase):
    @inlineCallbacks
    def test_close_after_start(self):
        tx = AmqpReconnectingFactory(**utils.generate_factory_config())
        yield tx.teardown()
