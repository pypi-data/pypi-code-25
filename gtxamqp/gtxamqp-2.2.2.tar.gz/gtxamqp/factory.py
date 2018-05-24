from __future__ import print_function
import os
from twisted.internet import protocol, reactor
from twisted.internet.defer import Deferred, inlineCallbacks, passthru, DeferredList
from twisted.internet.task import deferLater
from txamqp import spec
from txamqp.client import ChannelClosed
from gtxamqp.delegate import TwistedDelegate
from gtxamqp.facade import AmqpClient
from gtxamqp.connector import connectTCP
from twisted.internet.error import (ConnectionLost,
                                    ConnectionDone)
from protocol import AmqpProtocol


import logging

# The spec specifies that the maximum number of
# channels per connection is a 16-bit number.

# we pose a lower hard-limit of 8 bit, to ensure that a big amount of channels won't cause any hangs
# on the server side ( which happen in real life rabbitmq scenarios)

# you find find the limitation in "Limitations" section of the spec:
# amqp 0.8 spec: https://www.rabbitmq.com/resources/specs/amqp0-8.pdf
# amqp 0.9.1 spec: https://www.rabbitmq.com/resources/specs/amqp0-9-1.pdf


default_spec = 'amqp0-9-1.rabbitmq.xml'
# default_spec = 'amqp0-8.xml'
# default_spec = 'amqp0-8.stripped.rabbitmq.xml'
MAX_CHANNELS_PER_CONNECTION = 255

RECONNECTING_ERRORS = [ConnectionDone,
                       ConnectionLost,
                       ChannelClosed]


class AllChannelsAllocated(Exception):
    pass


class AmqpReconnectingFactory(protocol.ReconnectingClientFactory):
    protocol = AmqpProtocol

    def __init__(self, spec_file=None,
                 host='localhost', port=5672, user="guest",
                 prefetch=10,
                 password="guest", vhost="/",
                 post_teardown_func=None,
                 max_connection_retry_delay=3):
        spec_file = spec_file or os.path.join(os.path.dirname(__file__),
                                              "spec",
                                              default_spec)
        self.spec = spec.load(spec_file)
        self.user = user
        self.password = password
        self.vhost = vhost
        self.host = host
        self.prefetch = prefetch
        self.delegate = TwistedDelegate()
        self.deferred = self._create_call_deferred()
        self.logger = logging.getLogger(__name__)
        self.post_teardown_func = post_teardown_func
        self.clients = {}
        self.unused_client_ids = []
        self.p = None  # The protocol instance.
        self._consumers = {}
        self.maxDelay = max_connection_retry_delay
        self.connector = connectTCP(host=self.host,
                                    port=port,
                                    factory=self,
                                    reactor=reactor)

    def _create_call_deferred(self):
        """
        create a call deferred that traps reconnecting errors
        """
        def errors_to_trap(f):
            if f.type in RECONNECTING_ERRORS:
                f.trap(f.type)

        return Deferred().addErrback(errors_to_trap)

    def get_client(self, queue=None, exchange=None, binding=None):
        channel_id = self.get_available_channel_id()
        client = AmqpClient(factory=self,
                            channel_id=channel_id,
                            queue=queue,
                            binding=binding,
                            exchange=exchange,
                            teardown_func=self._remove_client)
        self.clients[channel_id] = client
        return client

    def get_available_channel_id(self):
        # each client holds one channel
        if len(self.clients) >= MAX_CHANNELS_PER_CONNECTION:
            # there aren't anymore channels to allocate
            msg = "max amount of clients per connection reached"
            raise AllChannelsAllocated(msg)

        # channel id's start at 1, while clients start at zero
        # if there are no clients, than the first client id should be 1
        client_id = self.unused_client_ids.pop() \
            if self.unused_client_ids else len(self.clients) + 1
        return client_id

    def _remove_client(self, client):
        # channel id's start at 1, while clients start at zero
        if client.channel_id in self.clients:
            self.unused_client_ids.append(client.channel_id)
            # instead of deleting items, we rehash the dict
            self.clients = {cid: c for cid, c in self.clients.items()
                            if cid != client.channel_id}

    def _start_consumers(self):
        dl = []
        for consumer, client in self._consumers.itervalues():
            dl.append(client.basic_consume(**consumer.conf))

        self._consumers = {}
        return DeferredList(dl)

    def _stop_consumers(self):
        for consumer, _ in self._consumers.values():
            consumer.stop()

    def add_consumer(self, client, consumer):
        self._consumers[consumer.consumer_tag] = (consumer, client)
        return consumer

    def remove_consumer(self, consumer_tag):
        if consumer_tag not in self._consumers:
            return

        consumer, client = self._consumers.pop(consumer_tag)
        return consumer

    def get_consumer_by_tag(self, consumer_tag):
        if consumer_tag not in self._consumers:
            return
        consumer, _ = self._consumers[consumer_tag]
        return consumer

    def _reconnect_on_fail(self, failure):
        if self.p:
            self.p.transport.loseConnection()

        self.p = None
        return failure

    def _get_call_deferred(self, method_name, *args, **kwargs):
        channel_id = kwargs.pop("channel_id", None)
        if channel_id:
            kwargs["channel"] = self.p.channels[channel_id]

        d = getattr(self.p, method_name)(*args, **kwargs)
        d.addErrback(self._reconnect_on_fail)
        return d

    def call_method(self, method_name, *args, **kwargs):
        if self.p and self.p.connected:
            return self._get_call_deferred(method_name, *args, **kwargs)

        if not self.deferred or self.deferred.called:
            self.deferred = self._create_call_deferred()

        self.deferred.addCallback(lambda *x: self.call_method(method_name,
                                                              *args,
                                                              **kwargs))

        return self.deferred

    def buildProtocol(self, addr):
        self.p = self.protocol(factory=self,
                               delegate=self.delegate,
                               vhost=self.vhost,
                               spec=self.spec)

        # sequence numbers are start at one
        self.p.message_seq_number = 1
        reactor.callLater(0, self._start_consumers)
        self.resetDelay()
        return self.p

    def startedConnecting(self, connector):

        @inlineCallbacks
        def resume_clients(*x):
            for c in self.clients.values():
                yield c.resume(force=True)

        # add initialize clients at the beginning
        # of the chain, to make sure everything is resumed
        # before firing all deferreds

        cbs = ((resume_clients, [], {}), (passthru, None, None))
        self.deferred.callbacks.insert(0, cbs)

        protocol.ReconnectingClientFactory.startedConnecting(self, connector)

    def clientConnectionFailed(self, connector, reason):
        self.p = None
        protocol.ReconnectingClientFactory.clientConnectionLost(self,
                                                                connector,
                                                                reason)

    def clientConnectionLost(self, connector, reason):
        self._stop_consumers()
        self.p = None
        protocol.ReconnectingClientFactory.clientConnectionFailed(self,
                                                                  connector,
                                                                  reason)

    def retry(self, connector=None):

        if self.deferred.called:
            msg = "retrying %s after successful connection..."
            self.logger.debug(msg, str(self))
            self.deferred = self._create_call_deferred()
        else:
            msg = "retrying %s before successful connection...",
            self.logger.debug(msg, str(self))

        for c in self.clients.values():
            self.logger.debug("pausing client %s...",
                              str(c))
            c.pause()

        protocol.ReconnectingClientFactory.retry(self, connector)

    @inlineCallbacks
    def teardown(self, *args):
        """
        close the factory gracefully.
        does not close before a connection has been made
        """
        deferred = deferLater(reactor, 0, lambda *x: None)
        if self.continueTrying and not self.deferred.called:
            self.deferred.addCallback(self.teardown)
            deferred = self.deferred
        else:
            # close the clients before disconnecting
            for c in self.clients.values():
                yield c.teardown()

            self.stopTrying()
            self.connector.disconnect()
            if self.p and self.p.connected:
                deferred = self.p.onConnectionLost

            if self.post_teardown_func:
                def post_teardown(*a, **kw):
                    return self.post_teardown_func(self)
                deferred.addBoth(post_teardown)

        yield deferred
