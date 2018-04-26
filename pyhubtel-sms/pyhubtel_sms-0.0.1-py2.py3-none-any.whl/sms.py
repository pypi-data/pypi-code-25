# -*- coding: utf-8 -*-

import requests
from requests import Session
from requests.auth import HTTPBasicAuth

from .exceptions import SMSError, InvalidMessageError
from .message import Message, Messages
from .utils import parse_time


class SMS(object):

    """Construct an SMS object.

    Args:
        client_id (str): unity API client ID.
        client_secret (str): unity API client secret.

    Attributes:
        client_id (str): unity API client ID.
        client_secret (str): unity API client secret.

    """

    def __init__(self, client_id=None, client_secret=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_base_url = "https://api.hubtel.com"
        self.api_version = "v1"
        self.status_code = None

    def __repr__(self):
        if self.status_code:
            return "<{name} [{status_code}] @{id:x}>".format(
                name=self.__class__.__name__,
                id=id(self) & 0xFFFFFF,
                status_code=self.status_code,
            )

        return "<{name} @{id:x}>".format(
            name=self.__class__.__name__, id=id(self) & 0xFFFFFF
        )

    def __auth_key(self):
        return HTTPBasicAuth(self.client_id, self.client_secret)

    @property
    def auth_key(self):
        """:obj:`HTTPBasicAuth`."""
        return self.__auth_key()

    def send(self, message):
        """Send an SMS.

        Args:
            message (:obj:`Message` or :obj:`Messages`): A user constructed
                :obj:`Message` or :obj:`Messages`.

        Returns:
            dict: sample::

                {
                  "ClientReference": "pyhubtel",
                  "MessageId": "d0c74524-e0a6-4c56-8afe-9cb1c23b636c",
                  "Status": 0,
                  "NetworkId": "62003",
                  "Rate": 1
                }

            or ::

                {
                  "Id": 648919,
                  "Name": "PyHubtel SMS Campaign",
                  "SenderId": "pyhubtel",
                  "Stats": {
                    "Pending": 2
                  },
                  "Status": "Scheduled",
                  "Time": "2018-03-23 07:41",
                  "TotalCount": 2
                }

        Raises:
            InvalidMessageError: If `message` is not an instance of
                :obj:`Message` or :obj:`Messages`.
            SMSError: If an SMS was not successfully sent.

        """
        try:
            body = message.body()
            auth = self.auth_key
            url = "{}/{}/{}".format(
                self.api_base_url, self.api_version, message.route
            )

            response = requests.post(url=url, json=body, auth=auth)
            self.status_code = response.status_code

            if 200 <= self.status_code < 203:
                return response.json()

            response.raise_for_status()
        except InvalidMessageError as e:
            raise InvalidMessageError(e)

        except requests.exceptions.RequestException as e:
            raise SMSError(e, response)

        except Exception as e:
            raise SMSError(e)

    @staticmethod
    def _courier(method, url, **kwargs):
        with Session() as session:
            return session.request(method=method, url=url, **kwargs)

    def _send(self, method, url, **kwargs):
        try:
            auth = self.auth_key
            response = self._courier(method, url, auth=auth, **kwargs)
            self.status_code = response.status_code

            if 200 <= self.status_code < 203:
                return response.json()

            if self.status_code == 204:
                return {}

            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise SMSError(e, response)

        except Exception as e:
            raise SMSError(e)

    def send_message(
        self,
        sender=None,
        recipient=None,
        content=None,
        time=None,
        registered_delivery=None,
        flash_message=None,
        reference=None,
    ):
        """Send an SMS to a single recipient.

        Args:
            sender (str): The sender name or address. `sender` must be 11
                characters or less without spaces or 16 numbers.

            recipient (str): The recipient phone number. This number must
                be in the international phone number format with a "+" as
                prefix. eg. +23350xxxxxxx. The local number format as given
                by the network provider is also accepted. eg. 050xxxxxxx.

            content (str): The contents of the message. This is required for
                all message types except WAP Push messages. Binary messages
                should use HEX string notation.

            time (str, optional): The scheduled time to send the message.
                Accepted inputs include:

                * 2018-03-23 10:27:24
                * 2018-03-23T10:27:24.5
                * Fri Mar 23 10:27:24
                * Fri Mar 23 10:27:24 2018
                * 2018 10:27:24 GMT 23 Mar Fri
                * Fri Mar 23 10:27:21 GMT 2018
                * Fri Mar 23
                * 10:27 am

            registered_delivery (bool, optional): A setting to indicate a
                delivery report request.

            flash_message (bool, optional): A setting to indicate if message
                must be sent as a flash message.

            reference (str, optional): A reference set by user for uniquely
                identifying this message. The reference will be sent as part
                of delivery report notifications.

        Returns:
            dict: sample::

                {
                  "ClientReference": "pyhubtel",
                  "MessageId": "d0c74524-e0a6-4c56-8afe-9cb1c23b636c",
                  "Status": 0,
                  "NetworkId": "62003",
                  "Rate": 1
                }

        """
        message = Message(
            sender=sender,
            recipient=recipient,
            content=content,
            time=time,
            registered_delivery=registered_delivery,
            flash_message=flash_message,
            reference=reference,
        )
        return self.send(message)

    def send_same_message_to_group(
        self,
        sender=None,
        recipients=None,
        content=None,
        campaign_name=None,
        time=None,
    ):
        """Send the same SMS to a group.

        Args:
            sender (str): The sender name or address. `sender` must be 11
                characters or less without spaces or 16 numbers.

            recipients (:obj:`list` of :obj:`str`): A list of recipient
                phone numbers. These numbers must be in the international phone
                number format with a "+" as prefix.
                eg. ['+23320xxxxxxx', '+23350xxxxxxx'].

                The local number format as given by the network provider is
                also accepted.
                eg. ['020xxxxxxx', '050xxxxxxx'].

            content (str): The content of the message. This is required for
                all message types except WAP Push messages. Binary messages
                should use HEX string notation.

            campaign_name (str): The name of a batch of SMS. This required for
                reporting purposes.

            time (str, optional): The scheduled time to send the message.
                Accepted inputs include:

                * 2018-03-23 10:27:24
                * 2018-03-23T10:27:24.5
                * Fri Mar 23 10:27:24
                * Fri Mar 23 10:27:24 2018
                * 2018 10:27:24 GMT 23 Mar Fri
                * Fri Mar 23 10:27:21 GMT 2018
                * Fri Mar 23
                * 10:27 am

        Returns:
            dict: sample::

                {
                  "Id": 648919,
                  "Name": "PyHubtel SMS Campaign",
                  "SenderId": "pyhubtel",
                  "Stats": {
                    "Pending": 2
                  },
                  "Status": "Scheduled",
                  "Time": "2018-03-23 07:41",
                  "TotalCount": 2
                }

        """
        message = Message(
            sender=sender,
            content=content,
            recipients=recipients,
            campaign_name=campaign_name,
            time=parse_time(time, drop_seconds=True),
        )
        return self.send(message)

    def send_personalized_message_to_group(
        self, sender=None, data=None, campaign_name=None, time=None
    ):
        """Send personalized SMS to a group.

        Args:
            sender (str): The sender name or address. `sender` must be 11
                characters or less without spaces or 16 numbers.

            data (:obj:`list` of :obj:`dict`): A list of dictionary objects
                each with the keys: 'recipient' and 'content'.
                eg.
                data = [
                    {'recipient': '020xxxxxxx', 'content': 'hello one'},
                    {'recipient': '050xxxxxxx', 'content': 'hello two'},
                ]

                or

                data = [
                    {'recipient': '+23320xxxxxxx', 'content': 'hello one'},
                    {'recipient': '+23350xxxxxxx', 'content': 'hello two'},
                ]

            campaign_name (str): The name of a batch of SMS. This required for
                reporting purposes.

            time (str, optional): The scheduled time to send the message.
                Accepted inputs include:

                * 2018-03-23 10:27:24
                * 2018-03-23T10:27:24.5
                * Fri Mar 23 10:27:24
                * Fri Mar 23 10:27:24 2018
                * 2018 10:27:24 GMT 23 Mar Fri
                * Fri Mar 23 10:27:21 GMT 2018
                * Fri Mar 23
                * 10:27 am

        Returns:
            dict: sample::

                {
                  "Id": 648919,
                  "Name": "PyHubtel SMS Campaign",
                  "SenderId": "pyhubtel",
                  "Stats": {
                    "Pending": 2
                  },
                  "Status": "Scheduled",
                  "Time": "2018-03-23 07:41",
                  "TotalCount": 2
                }

        Raises:
            InvalidMessageError: If `data` is malformed ie. missing the
                required keys.

        """
        try:
            batch = [
                Message(
                    recipient=each.get("recipient"),
                    content=each.get("content"),
                )
                for each in data
            ]

            messages = Messages(
                sender=sender,
                campaign_name=campaign_name,
                batch=batch,
                time=parse_time(time, drop_seconds=True),
            )
            return self.send(messages)

        except KeyError as e:
            raise InvalidMessageError(e)

    def get_message_info(self, message_id):
        """Retrieve details of a message to a single recipient.

        Args:
            message_id (str): A unique identifier for each message. This can
                be the UUID or GUID of that message.

        Returns:
            dict: sample::

                {
                  "Rate":1,
                  "Units":1,
                  "MessageId":"76341c98-ee94-4f6c-d861-ac4254d9aac6",
                  "Content":"Hello world.",
                  "Status":"Delivered",
                  "NetworkId":"62001",
                  "UpdateTime":"2018-03-12 11:43:05",
                  "Time":"2018-03-12 11:43:00",
                  "To":"+233502345678",
                  "From":"pyhubtel"
                }

        """
        url = "{}/{}/messages/{}".format(
            self.api_base_url, self.api_version, message_id
        )
        return self._send("get", url)

    @staticmethod
    def _refine_query_messages(data, limit):
        """Cleans up data by returning only the values of the 'Messages' key.
        """
        if isinstance(data, dict):
            return data.get("Messages")[:limit]

        return False

    def query_messages(
        self,
        start=None,
        end=None,
        skip=None,
        limit=None,
        pending=None,
        direction=None,
    ):
        """Retrieve an overview of all SMS sent or received by an account.

        Note:
            You may query within 5 second intervals. Attempts to execute at
            smaller intervals will result in being banned for a while.

        Args:
            start (str, optional): The date to start querying from.
                Accepted inputs include:

                * 2018-03-23 10:27:24
                * 2018-03-23T10:27:24.5
                * Fri Mar 23 10:27:24
                * Fri Mar 23 10:27:24 2018
                * 2018 10:27:24 GMT 23 Mar Fri
                * Fri Mar 23 10:27:21 GMT 2018
                * Fri Mar 23
                * 10:27 am

            end (str, optional): The last possible time in the query.
                Accepted inputs; same as `start` parameter.

            skip (int, optional): The number of results to skip from the
                result set. Results are in chronological order (oldest first).
                Defaults to 0.

            limit (int, optional): The maximum number of results to return.
                Defaults to 100.

            pending (bool, optional): A True or False flag used to
                indicate if only scheduled messages should be returned in the
                result set. By default only sent message are returned.

            direction (str, optional): A filter for the result by the direction
                of the message.

                Possible values are 'in' (for only inbound messages) and
                'out' (for only outbound messages).

        Returns:
            list: sample::

                [
                    {
                      "Status": "Delivered",
                      "From": "pyhubtel",
                      "To": "+233552345678",
                      "Content": "Hi there.",
                      "Direction": "out",
                      "Units": 1,
                      "NetworkId": "62001",
                      "UpdateTime": "2018-03-08 11:35:02",
                      "Rate": 1,
                      "Time": "2018-03-08 11:34:42",
                      "MessageId": "5ec6bbc2-c977-4a0d-ac32-8743e89cf6f9"
                    }, ...
                ]

        """
        if skip is None:
            skip = 0

        if limit is None:
            limit = 100

        url = "{}/{}/messages?index={}".format(
            self.api_base_url, self.api_version, skip
        )

        if start:
            url = "{}&start={}".format(url, parse_time(start))
        if end:
            url = "{}&end={}".format(url, parse_time(end))
        if pending:
            url = "{}&pending={}".format(url, pending)
        if direction:
            url = "{}&direction={}".format(url, direction)

        return self._refine_query_messages(self._send("get", url), limit)

    def reschedule_message(self, message_id=None, time=None):
        """Reschedule an unsent message.

        Args:
            message_id (str): A unique identifier for each message. This can
                be the UUID or GUID of that message.

            time (str): The scheduled time to send the message.
                Accepted inputs include:

                * 2018-03-23 10:27:24
                * 2018-03-23T10:27:24.5
                * Fri Mar 23 10:27:24
                * Fri Mar 23 10:27:24 2018
                * 2018 10:27:24 GMT 23 Mar Fri
                * Fri Mar 23 10:27:21 GMT 2018
                * Fri Mar 23
                * 10:27 am

        Returns:
            dict: sample::

                {
                  "Time": "2018-03-14 08:00:00"
                }

        """
        url = "{}/{}/messages/{}".format(
            self.api_base_url, self.api_version, message_id
        )

        data = {"Time": parse_time(time)}
        return self._send("put", url, json=data)

    def cancel_message(self, message_id):
        """Cancel a scheduled message to single recipient.

        Note:
            The cancellation request will fail if the message has already
            been sent.

        Args:
            message_id (str): A unique identifier for each message. This can
                be the UUID or GUID of that message.

        """
        url = "{}/{}/messages/{}".format(
            self.api_base_url, self.api_version, message_id
        )
        return self._send("delete", url)

    def get_bulk_message_info(self, message_id):
        """Retrieve details of a message to a group.

        Args:
            message_id (str): A unique identifier for each message. This can
                be the UUID or GUID of that message.

        Returns:
            dict: sample::

                {
                  "Id":651583,
                  "TotalCount":2,
                  "Stats":{
                    "Delivery":{
                      "Delivered":2,
                      "Error":0
                    },
                    "Billing":[
                      {
                        "Unbilled":0,
                        "Billed":2,
                        "Revenue":2,
                        "Network":"62001"
                      }
                    ]
                  },
                  "Status":"Sent",
                  "SentTime":"2018-03-12T10:19:50.4470000",
                  "Name":"PyHubtel SMS Campaign",
                  "SenderId":"pyhubtel",
                  "Time":"2018-03-12 08:50"
                }

        """
        url = "{}/{}/batches/{}".format(
            self.api_base_url, self.api_version, message_id
        )
        return self._send("get", url)

    def cancel_bulk_message(self, message_id):
        """Cancel a scheduled message to a group.

        Note:
            The cancellation request will fail if the message has already
            been sent.

        Args:
            message_id (str): A unique identifier for each message. This can
                be the UUID or GUID of that message.

        """
        url = "{}/{}/batches/{}".format(
            self.api_base_url, self.api_version, message_id
        )
        return self._send("delete", url)
