# coding: utf-8

"""
    Wavefront Public API

    <p>The Wavefront public API enables you to interact with Wavefront servers using standard web service API tools. You can use the API to automate commonly executed operations such as automatically tagging sources.</p><p>When you make API calls outside the Wavefront API documentation you must add the header \"Authorization: Bearer &lt;&lt;API-TOKEN&gt;&gt;\" to your HTTP requests.</p><p>For legacy versions of the Wavefront API, see the <a href=\"/api-docs/ui/deprecated\">legacy API documentation</a>.</p>

    OpenAPI spec version: v2
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from pprint import pformat
from six import iteritems
import re


class ResponseContainerPagedAlert(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'status': 'ResponseStatus',
        'response': 'PagedAlert'
    }

    attribute_map = {
        'status': 'status',
        'response': 'response'
    }

    def __init__(self, status=None, response=None):
        """
        ResponseContainerPagedAlert - a model defined in Swagger
        """

        self._status = None
        self._response = None
        self.discriminator = None

        self.status = status
        self.response = response

    @property
    def status(self):
        """
        Gets the status of this ResponseContainerPagedAlert.

        :return: The status of this ResponseContainerPagedAlert.
        :rtype: ResponseStatus
        """
        return self._status

    @status.setter
    def status(self, status):
        """
        Sets the status of this ResponseContainerPagedAlert.

        :param status: The status of this ResponseContainerPagedAlert.
        :type: ResponseStatus
        """
        if status is None:
            raise ValueError("Invalid value for `status`, must not be `None`")

        self._status = status

    @property
    def response(self):
        """
        Gets the response of this ResponseContainerPagedAlert.

        :return: The response of this ResponseContainerPagedAlert.
        :rtype: PagedAlert
        """
        return self._response

    @response.setter
    def response(self, response):
        """
        Sets the response of this ResponseContainerPagedAlert.

        :param response: The response of this ResponseContainerPagedAlert.
        :type: PagedAlert
        """
        if response is None:
            raise ValueError("Invalid value for `response`, must not be `None`")

        self._response = response

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        if not isinstance(other, ResponseContainerPagedAlert):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
