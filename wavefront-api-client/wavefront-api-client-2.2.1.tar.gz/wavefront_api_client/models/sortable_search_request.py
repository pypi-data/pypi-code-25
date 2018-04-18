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


class SortableSearchRequest(object):
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
        'limit': 'int',
        'offset': 'int',
        'query': 'list[SearchQuery]',
        'sort': 'Sorting'
    }

    attribute_map = {
        'limit': 'limit',
        'offset': 'offset',
        'query': 'query',
        'sort': 'sort'
    }

    def __init__(self, limit=None, offset=None, query=None, sort=None):
        """
        SortableSearchRequest - a model defined in Swagger
        """

        self._limit = None
        self._offset = None
        self._query = None
        self._sort = None
        self.discriminator = None

        if limit is not None:
          self.limit = limit
        if offset is not None:
          self.offset = offset
        if query is not None:
          self.query = query
        if sort is not None:
          self.sort = sort

    @property
    def limit(self):
        """
        Gets the limit of this SortableSearchRequest.
        The number of results to return.  Default: 100

        :return: The limit of this SortableSearchRequest.
        :rtype: int
        """
        return self._limit

    @limit.setter
    def limit(self, limit):
        """
        Sets the limit of this SortableSearchRequest.
        The number of results to return.  Default: 100

        :param limit: The limit of this SortableSearchRequest.
        :type: int
        """

        self._limit = limit

    @property
    def offset(self):
        """
        Gets the offset of this SortableSearchRequest.
        The number of results to skip before returning values.  Default: 0

        :return: The offset of this SortableSearchRequest.
        :rtype: int
        """
        return self._offset

    @offset.setter
    def offset(self, offset):
        """
        Sets the offset of this SortableSearchRequest.
        The number of results to skip before returning values.  Default: 0

        :param offset: The offset of this SortableSearchRequest.
        :type: int
        """

        self._offset = offset

    @property
    def query(self):
        """
        Gets the query of this SortableSearchRequest.
        A list of queries by which to limit the search results.  Entities that match ALL queries in the list are returned

        :return: The query of this SortableSearchRequest.
        :rtype: list[SearchQuery]
        """
        return self._query

    @query.setter
    def query(self, query):
        """
        Sets the query of this SortableSearchRequest.
        A list of queries by which to limit the search results.  Entities that match ALL queries in the list are returned

        :param query: The query of this SortableSearchRequest.
        :type: list[SearchQuery]
        """

        self._query = query

    @property
    def sort(self):
        """
        Gets the sort of this SortableSearchRequest.

        :return: The sort of this SortableSearchRequest.
        :rtype: Sorting
        """
        return self._sort

    @sort.setter
    def sort(self, sort):
        """
        Sets the sort of this SortableSearchRequest.

        :param sort: The sort of this SortableSearchRequest.
        :type: Sorting
        """

        self._sort = sort

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
        if not isinstance(other, SortableSearchRequest):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
