from typing import Dict

import boto3

from elife_bus_sdk.events import Event
from elife_bus_sdk.publishers.event_publisher import EventPublisher


class SNSPublisher(EventPublisher):
    name = 'sns'

    def __init__(self, region: str = '', subscriber: str = '', name: str = '',
                 env: str = '', **overrides) -> None:
        """
        Allows publication of `Message` objects to a target AWS SNS Topic

        :param region: str
        :param subscriber: str
        :param name: str
        :param env: str
        :param overrides: dict: Any boto3.resource override values that you would like to pass
        """
        self._arn = self._create_arn(region, subscriber, name, env)
        self._resource = boto3.resource(self.name, **overrides)

    @property
    def arn(self):
        return self._arn

    @staticmethod
    def _create_arn(region: str, subscriber: str, name: str, env: str) -> str:
        """
        :param region: str
        :param subscriber: str
        :param name: str
        :param env: str
        :return: str
        """
        return 'arn:aws:sns:{region}:{subscriber}:{name}--{env}'.format(region=region,
                                                                        subscriber=subscriber,
                                                                        name=name,
                                                                        env=env)

    def publish(self, event: Event) -> Dict:
        """
        Publishes a JSON representation of `Event` object to the target AWS SNS Topic.

        :param event: :class: `Event`
        :return: dict:

        example return value:
        {
            'MessageId': '5fddaf2c-be65-46cc-bbe3-1ceb960db794',
            'ResponseMetadata': {
                'HTTPHeaders': {
                    'content-length': '327',
                    '13:24:37 GMT'
                },
                'HTTPStatusCode': 200,
                'RequestId': 'c90cb103-16a5-4f9d-a23f-2ae1b0dba896',
                'RetryAttempts': 0
            }
        }
        """
        return self._resource.Topic(self._arn).publish(Message=event.to_json())
