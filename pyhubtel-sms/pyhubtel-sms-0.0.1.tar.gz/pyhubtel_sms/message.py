# -*- coding: utf-8 -*-

from .utils import parse_phone_number, parse_time, prune
from .exceptions import InvalidMessageError


class MessageMixin(object):

    """Message mixin."""

    def __repr__(self):
        return "<{name} @{id:x}>".format(
            name=self.__class__.__name__, id=id(self) & 0xFFFFFF
        )

    def body(self):
        """Constructs the required dictionary object for :obj:`Message`
        and :obj:`Messages`.

        Returns:
            dict

        Raises:
            InvalidMessageError: If dictionary object was not successfully
                constructed.

        """
        if isinstance(self, Message):
            # send the same message to different recipients.
            try:
                data = [
                    {
                        "Content": self.content,
                        "Recipients": [
                            {"MobileNumber": parse_phone_number(each)}
                            for each in self.recipients
                        ],
                    }
                ]

                body = {
                    "SenderId": self.sender,
                    "Name": self.campaign_name,
                    "Groups": data,
                    "Time": parse_time(self.time, drop_seconds=True),
                }

                return prune(body)

            except (TypeError, AttributeError):
                try:
                    # send message to a single recipient.
                    body = {
                        "From": self.sender,
                        "To": parse_phone_number(self.recipient),
                        "Content": self.content,
                        "RegisteredDelivery": self.registered_delivery,
                        "Time": parse_time(self.time),
                        "FlashMessage": self.flash_message,
                        "ClientReference": self.reference,
                    }

                    return prune(body)

                except AttributeError as e:
                    raise InvalidMessageError(e)

        if isinstance(self, Messages):
            # send different messages to different recipients.
            try:
                data = [
                    {
                        "Content": each.content,
                        "Recipients": [
                            {
                                "MobileNumber": parse_phone_number(
                                    each.recipient
                                )
                            }
                        ],
                    }
                    for each in self.batch
                ]

                body = {
                    "SenderId": self.sender,
                    "Name": self.campaign_name,
                    "Groups": data,
                    "Time": parse_time(self.time, drop_seconds=True),
                }

                return prune(body)

            except (TypeError, AttributeError) as e:
                raise InvalidMessageError(e)

    @property
    def is_bulk(self):
        """bool: Tags object as message to a single recipient or multiple
        recipients (batch/bulk message).
        """
        try:
            if isinstance(self, Messages):
                return True

            if self.recipients:
                return True

        except AttributeError:
            pass
        return False

    @property
    def route(self):
        """str: Tags object with route to use when message is being sent."""
        if self.is_bulk:
            return "batches"

        return "messages"


class Message(MessageMixin):

    """Construct a message object.

    Note:
        Use either `recipient` or `recipients` parameter but not both.
        Use `recipient` when constructing a message object intended for a
        single recipient and `recipients` when the message is intended for
        multiple recipients.

    Args:
        sender (str): The sender name or address. `sender` must be 11
            characters or less without spaces or 16 numbers.

        recipient (str): The recipient phone number. This number must be in
            the international phone number format with a "+" as prefix.
            eg. +23350xxxxxxx. The local number format as given by the network
            provider is also accepted. eg. 050xxxxxxx.

        recipients (:obj:`list` of :obj:`str`): A list of recipient phone
            numbers. These numbers must be in the international phone number
            format with a "+" as prefix.
            eg. ['+23320xxxxxxx', '+23350xxxxxxx'].

            The local number format as given by the network provider is
            also accepted.
            eg. ['020xxxxxxx', '050xxxxxxx'].

        content (str): The content of the message. This is required for all
            message types except WAP Push messages. Binary messages should use
            HEX string notation.

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

        registered_delivery (bool, optional): A setting to indicate a delivery
            report request.

        flash_message (bool, optional): A setting to indicate if message
            must be sent as a flash message.

        reference (str, optional): A reference set by user for uniquely
            identifying this message. The reference will be sent as part of
            delivery report notifications.

    """

    def __init__(
        self,
        sender=None,
        recipient=None,
        recipients=None,
        content=None,
        campaign_name=None,
        time=None,
        registered_delivery=None,
        flash_message=None,
        reference=None,
    ):
        self.sender = sender
        self.recipient = recipient
        self.recipients = recipients
        self.content = content
        self.campaign_name = campaign_name
        self.time = time
        self.registered_delivery = registered_delivery
        self.flash_message = flash_message
        self.reference = reference


class Messages(MessageMixin):

    """Construct a batch/bulk message.

    This creates a messages object intended for sending messages to multiple
    recipients each with a different content.

    Args:
        sender (str): The sender name or address. `sender` must be 11
            characters or less without spaces or 16 numbers.

        campaign_name (str): The name of a batch of SMS. This required for
            reporting purposes.

        batch (:obj:`list` of :obj:`Message`): A list of message objects each
            with a different recipient and content.

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

    """

    def __init__(self, sender=None, campaign_name=None, batch=None, time=None):
        self.sender = sender
        self.campaign_name = campaign_name
        self.batch = batch
        self.time = time
