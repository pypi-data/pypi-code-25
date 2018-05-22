# -*- coding: utf-8 -*-

"""
    message_media_webhooks.models.update_webhook_request

    This file was automatically generated for MessageMedia by APIMATIC v2.0 ( https://apimatic.io )
"""


class UpdateWebhookRequest(object):

    """Implementation of the 'Update Webhook request' model.

    TODO: type model description here.

    Attributes:
        url (string): TODO: type description here.
        method (string): TODO: type description here.
        encoding (string): TODO: type description here.
        events (list of string): TODO: type description here.
        template (string): TODO: type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "url":'url',
        "method":'method',
        "encoding":'encoding',
        "events":'events',
        "template":'template'
    }

    def __init__(self,
                 url=None,
                 method=None,
                 encoding=None,
                 events=None,
                 template=None):
        """Constructor for the UpdateWebhookRequest class"""

        # Initialize members of the class
        self.url = url
        self.method = method
        self.encoding = encoding
        self.events = events
        self.template = template


    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        url = dictionary.get('url')
        method = dictionary.get('method')
        encoding = dictionary.get('encoding')
        events = dictionary.get('events')
        template = dictionary.get('template')

        # Return an object of this model
        return cls(url,
                   method,
                   encoding,
                   events,
                   template)


