# coding: utf-8

"""
    Wavefront Public API

    <p>Wavefront public APIs enable you to interact with Wavefront servers using standard web service API tools. You can use the APIs to automate commonly executed operations such as automatically tagging sources.</p><p>When you make API calls outside the Wavefront UI you must add the header \"Authorization: Bearer &lt;&lt;API-TOKEN&gt;&gt;\" to your HTTP requests.</p><p>For legacy versions of the Wavefront API, see the <a href=\"/api-docs/ui/deprecated\">legacy API documentation</a>.</p>

    OpenAPI spec version: v2
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from pprint import pformat
from six import iteritems
import re


class QueryKeyContainer(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, name=None, metric=None, host=None, tags=None, host_tag=None):
        """
        QueryKeyContainer - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'name': 'str',
            'metric': 'str',
            'host': 'str',
            'tags': 'dict(str, str)',
            'host_tag': 'str'
        }

        self.attribute_map = {
            'name': 'name',
            'metric': 'metric',
            'host': 'host',
            'tags': 'tags',
            'host_tag': 'hostTag'
        }

        self._name = name
        self._metric = metric
        self._host = host
        self._tags = tags
        self._host_tag = host_tag

    @property
    def name(self):
        """
        Gets the name of this QueryKeyContainer.

        :return: The name of this QueryKeyContainer.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this QueryKeyContainer.

        :param name: The name of this QueryKeyContainer.
        :type: str
        """

        self._name = name

    @property
    def metric(self):
        """
        Gets the metric of this QueryKeyContainer.

        :return: The metric of this QueryKeyContainer.
        :rtype: str
        """
        return self._metric

    @metric.setter
    def metric(self, metric):
        """
        Sets the metric of this QueryKeyContainer.

        :param metric: The metric of this QueryKeyContainer.
        :type: str
        """

        self._metric = metric

    @property
    def host(self):
        """
        Gets the host of this QueryKeyContainer.

        :return: The host of this QueryKeyContainer.
        :rtype: str
        """
        return self._host

    @host.setter
    def host(self, host):
        """
        Sets the host of this QueryKeyContainer.

        :param host: The host of this QueryKeyContainer.
        :type: str
        """

        self._host = host

    @property
    def tags(self):
        """
        Gets the tags of this QueryKeyContainer.

        :return: The tags of this QueryKeyContainer.
        :rtype: dict(str, str)
        """
        return self._tags

    @tags.setter
    def tags(self, tags):
        """
        Sets the tags of this QueryKeyContainer.

        :param tags: The tags of this QueryKeyContainer.
        :type: dict(str, str)
        """

        self._tags = tags

    @property
    def host_tag(self):
        """
        Gets the host_tag of this QueryKeyContainer.

        :return: The host_tag of this QueryKeyContainer.
        :rtype: str
        """
        return self._host_tag

    @host_tag.setter
    def host_tag(self, host_tag):
        """
        Sets the host_tag of this QueryKeyContainer.

        :param host_tag: The host_tag of this QueryKeyContainer.
        :type: str
        """

        self._host_tag = host_tag

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
        if not isinstance(other, QueryKeyContainer):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
