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


class TargetInfo(object):
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
        'method': 'str',
        'id': 'str',
        'name': 'str'
    }

    attribute_map = {
        'method': 'method',
        'id': 'id',
        'name': 'name'
    }

    def __init__(self, method=None, id=None, name=None):
        """
        TargetInfo - a model defined in Swagger
        """

        self._method = None
        self._id = None
        self._name = None
        self.discriminator = None

        if method is not None:
          self.method = method
        if id is not None:
          self.id = id
        if name is not None:
          self.name = name

    @property
    def method(self):
        """
        Gets the method of this TargetInfo.
        Notification method of the alert target

        :return: The method of this TargetInfo.
        :rtype: str
        """
        return self._method

    @method.setter
    def method(self, method):
        """
        Sets the method of this TargetInfo.
        Notification method of the alert target

        :param method: The method of this TargetInfo.
        :type: str
        """
        allowed_values = ["EMAIL", "PAGERDUTY", "WEBHOOK"]
        if method not in allowed_values:
            raise ValueError(
                "Invalid value for `method` ({0}), must be one of {1}"
                .format(method, allowed_values)
            )

        self._method = method

    @property
    def id(self):
        """
        Gets the id of this TargetInfo.
        ID of the alert target

        :return: The id of this TargetInfo.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this TargetInfo.
        ID of the alert target

        :param id: The id of this TargetInfo.
        :type: str
        """

        self._id = id

    @property
    def name(self):
        """
        Gets the name of this TargetInfo.
        Name of the alert target

        :return: The name of this TargetInfo.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this TargetInfo.
        Name of the alert target

        :param name: The name of this TargetInfo.
        :type: str
        """

        self._name = name

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
        if not isinstance(other, TargetInfo):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
