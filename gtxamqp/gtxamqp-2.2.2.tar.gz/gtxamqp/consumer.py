import logging
import uuid

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
from txamqp.queue import Empty

from gtxamqp.utils import format_failure

logger = logging.getLogger(__name__)


class MissingProtocol(Exception):
    pass


class Consumer(object):
    def __init__(self,
                 factory,
                 channel_id,
                 queue_name,
                 callback,
                 errback=None,
                 no_ack=False,
                 consumer_tag=None):
        """
        initializes a consumer
        :param factory: the factory to use in order to create the consumer
        :param channel_id: the channel id of the channel to use
        :param queue_name: the queue name to bind to
        :param no_ack: make sure messages aren't acknowledged. if confirm is set,
        then no_ack overwrites confirm.
        :param callback: a callback to fire once a message exists
        :param consumer_tag: a specific consumer tag to use when creating the consumer
        """
        self.no_ack = no_ack
        self.factory = factory
        self.callback = callback
        self.errback = errback
        self.channel_id = channel_id
        self.consumer_tag = consumer_tag
        self.consumer_queue = None
        self.queue_name = queue_name
        self.running = False
        self.consumer = LoopingCall(self.consume_message)

    def __str__(self):
        return "{}-{}".format(hex(id(self)), self.channel_id)

    @property
    def conf(self):
        """
        returns this consumers configuration
        """
        return dict(callback=self.callback,
                    queue=self.queue_name,
                    no_ack=self.no_ack,
                    consumer_tag=self.consumer_tag)

    @inlineCallbacks
    def reset(self):
        """
        restarts the consumer
        """
        self.stop()
        self.consumer_queue = None

        yield self.start()

    @property
    def protocol(self):
        """
        returns the factory's protocol
        """
        return self.factory.p

    @inlineCallbacks
    def _initialize(self):
        if not self.protocol:
            raise MissingProtocol()
        channel = self.protocol.channels[self.channel_id]
        channel.in_confirm_mode = not self.no_ack
        consumer_tag = self.consumer_tag \
            or "-".join(["gctxqmp.ctag", str(uuid.uuid4())])
        msg = yield channel.basic_consume(queue=self.queue_name,
                                          no_ack=self.no_ack,
                                          consumer_tag=consumer_tag)
        self.consumer_tag = msg.consumer_tag
        self.consumer_queue = yield self.factory.p.queue(self.consumer_tag)

        if msg.content:
            reactor.callLater(0, self.callback, msg)

    @inlineCallbacks
    def start(self, interval=0):
        """
        start this consumer -
        * initialize the consumer
        * start consuming messages every given interval
        """
        try:
            if not self.consumer_queue:
                yield self._initialize()

            self.consumer.start(interval)
            self.running = True
        except Exception as e:
            logger.error("Failed on start consumer %s: %s",
                         str(self),
                         e.message)

    @inlineCallbacks
    def stop(self):
        """
        stop this consumer
        """
        self.running = False
        if self.consumer.running:
            yield self.consumer.stop()
            yield self.consumer_queue.close()

    def _on_error(self, failure):
        # queue is empty, don't log anything
        if failure.type is Empty:
            return

        # if errback is set, always call it
        if self.errback:
            self.errback(failure)
            return

        # don't log errors when not running
        if not self.running:
            return

        logger.error("consumer queue %s error: %s",
                     self.consumer_tag,
                     format_failure(failure))

    def _on_message(self, msg):
        if msg.content:
            msg.__dict__["no_ack"] = self.no_ack
            return msg

    def consume_message(self):
        """
        perform a consume operation
        """
        d = self.consumer_queue.get(timeout=5).addCallback(self._on_message)
        d.addCallback(self.callback)
        d.addErrback(self._on_error)
        return d
