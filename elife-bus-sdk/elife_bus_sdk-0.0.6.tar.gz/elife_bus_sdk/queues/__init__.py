from typing import Dict

from elife_bus_sdk.queues.sqs_queue import SQSMessageQueue
from elife_bus_sdk.queues.message_queue import MessageQueue


# list of queue classes you want to make available
QUEUES = (
    SQSMessageQueue,
)


def get_queue_types() -> Dict[str, MessageQueue]:
    return {q.name: q for q in QUEUES}


__all__ = [
    'get_queue_types',
    'MessageQueue',
    'SQSMessageQueue',
]
