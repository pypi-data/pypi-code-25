from __future__ import print_function
from twisted.internet.defer import inlineCallbacks
from txamqp.client import TwistedDelegate as VanillaTwistedDelegate


class TwistedDelegate(VanillaTwistedDelegate):
    @inlineCallbacks
    def basic_ack(self, ch, msg):
        if ch.in_confirm_mode and \
           msg.delivery_tag in ch.not_confirmed:
            yield ch.basic_ack(msg.delivery_tag)
            ch.not_confirmed.remove(msg.delivery_tag)

    def basic_recover_ok(self, ch, msg):
        """
        Confirm recovery.
        This method acknowledges a Basic.Recover method.
        """
        pass
