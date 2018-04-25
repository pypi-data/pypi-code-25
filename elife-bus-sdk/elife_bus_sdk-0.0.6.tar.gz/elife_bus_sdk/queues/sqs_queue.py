from typing import Dict, Generator, List

import boto3

from elife_bus_sdk.events import Event
from elife_bus_sdk.queues.message_queue import MessageQueue


class SQSMessageQueue(MessageQueue):
    name = 'sqs'
    _polling = False
    _stop_polling = False

    def __init__(self, **overrides):
        self._queue_name = overrides.pop('queue_name', None)
        self._overrides = overrides
        self._resource = boto3.resource(self.name, **self._overrides)
        self._queue = self._resource.get_queue_by_name(QueueName=self._queue_name)

    def dequeue(self) -> List[Event]:
        """Retrieves one or more messages (up to 10), from the queue.

        :return: list
        """
        conf = self._overrides
        msgs = self._queue.receive_messages(MaxNumberOfMessages=conf.get('MaxNumberOfMessages', 1),
                                            VisibilityTimeout=conf.get('VisibilityTimeout', 60),
                                            WaitTimeSeconds=conf.get('WaitTimeSeconds', 20))

        return [Event(**self._parse_message(msg)) for msg in msgs]

    def enqueue(self, message: str) -> Dict[str, str]:
        """Delivers a message to the queue.

        :param message: str
        :return: dict

        example return value:
        {
            'MD5OfMessageBody': 'string',
            'MD5OfMessageAttributes': 'string',
            'MessageId': 'string',
            'SequenceNumber': 'string'
        }
        """
        return self._queue.send_message(MessageBody=message)

    def is_polling(self) -> bool:
        """Return current polling state.

        :return:
        """
        return self._polling

    @staticmethod
    def _parse_message(message: 'sqs.Message') -> Dict[str, str]:
        """Parse a `sqs.Message` object and return a `dict` representation.

        :param message: :class: sqs.Message
        :return: dict
        """
        return {
            'body': message.body,
            'md5_of_body': message.md5_of_body,
            'message_id': message.message_id,
            'queue_url': message.queue_url,
            'receipt_handle': message.receipt_handle
        }

    def poll(self) -> Generator[Event, None, None]:
        """An infinite poll on the given queue object.

        Blocks for `WaitTimeSeconds` seconds before connection is dropped and re-established.

        :return: generator
        """
        # signal that instance is currently polling
        self._polling = True

        while not self._stop_polling:
            messages = self.dequeue()

            if not messages:
                continue

            try:
                yield messages[0]
            except (AttributeError, IndexError):
                yield Event()

        # finished, reset polling flag(s) for next poll call
        self._stop_polling = False
        self._polling = False

    @property
    def queue(self) -> 'sqs.Queue':
        """Returns the current `sqs.Queue` instance for the class.

        Any additional `boto3.sqs.Queue` functionality can be accessed by using this
        object directly.

        :return: :class: `sqs.Queue`
        """
        return self._queue

    def stop_polling(self) -> None:
        """Set `_stop_polling` flag to True signalling an active poll call to exit.

        :return:
        """
        self._stop_polling = True
