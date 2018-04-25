from typing import Dict

from elife_bus_sdk.publishers.event_publisher import EventPublisher
from elife_bus_sdk.publishers import sns_publisher
from elife_bus_sdk.publishers.sns_publisher import SNSPublisher


# list of publisher classes you want to make available
PUBLISHERS = [
    SNSPublisher
]


def get_publisher_types() -> Dict[str, EventPublisher]:
    return {pub.name: pub for pub in PUBLISHERS}


__all__ = [
    'EventPublisher',
    'sns_publisher',
    'SNSPublisher',
    'get_publisher_types'
]
