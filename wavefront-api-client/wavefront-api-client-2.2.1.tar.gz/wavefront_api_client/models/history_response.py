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


class HistoryResponse(object):
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
        'items': 'list[HistoryEntry]',
        'offset': 'int',
        'limit': 'int',
        'cursor': 'str',
        'total_items': 'int',
        'more_items': 'bool',
        'sort': 'Sorting'
    }

    attribute_map = {
        'items': 'items',
        'offset': 'offset',
        'limit': 'limit',
        'cursor': 'cursor',
        'total_items': 'totalItems',
        'more_items': 'moreItems',
        'sort': 'sort'
    }

    def __init__(self, items=None, offset=None, limit=None, cursor=None, total_items=None, more_items=None, sort=None):
        """
        HistoryResponse - a model defined in Swagger
        """

        self._items = None
        self._offset = None
        self._limit = None
        self._cursor = None
        self._total_items = None
        self._more_items = None
        self._sort = None
        self.discriminator = None

        if items is not None:
          self.items = items
        if offset is not None:
          self.offset = offset
        if limit is not None:
          self.limit = limit
        if cursor is not None:
          self.cursor = cursor
        if total_items is not None:
          self.total_items = total_items
        if more_items is not None:
          self.more_items = more_items
        if sort is not None:
          self.sort = sort

    @property
    def items(self):
        """
        Gets the items of this HistoryResponse.
        List of requested items

        :return: The items of this HistoryResponse.
        :rtype: list[HistoryEntry]
        """
        return self._items

    @items.setter
    def items(self, items):
        """
        Sets the items of this HistoryResponse.
        List of requested items

        :param items: The items of this HistoryResponse.
        :type: list[HistoryEntry]
        """

        self._items = items

    @property
    def offset(self):
        """
        Gets the offset of this HistoryResponse.

        :return: The offset of this HistoryResponse.
        :rtype: int
        """
        return self._offset

    @offset.setter
    def offset(self, offset):
        """
        Sets the offset of this HistoryResponse.

        :param offset: The offset of this HistoryResponse.
        :type: int
        """

        self._offset = offset

    @property
    def limit(self):
        """
        Gets the limit of this HistoryResponse.

        :return: The limit of this HistoryResponse.
        :rtype: int
        """
        return self._limit

    @limit.setter
    def limit(self, limit):
        """
        Sets the limit of this HistoryResponse.

        :param limit: The limit of this HistoryResponse.
        :type: int
        """

        self._limit = limit

    @property
    def cursor(self):
        """
        Gets the cursor of this HistoryResponse.
        The id at which the current (limited) search can be continued to obtain more matching items

        :return: The cursor of this HistoryResponse.
        :rtype: str
        """
        return self._cursor

    @cursor.setter
    def cursor(self, cursor):
        """
        Sets the cursor of this HistoryResponse.
        The id at which the current (limited) search can be continued to obtain more matching items

        :param cursor: The cursor of this HistoryResponse.
        :type: str
        """

        self._cursor = cursor

    @property
    def total_items(self):
        """
        Gets the total_items of this HistoryResponse.
        An estimate (lower-bound) of the total number of items available for return.  May not be a tight estimate for facet queries

        :return: The total_items of this HistoryResponse.
        :rtype: int
        """
        return self._total_items

    @total_items.setter
    def total_items(self, total_items):
        """
        Sets the total_items of this HistoryResponse.
        An estimate (lower-bound) of the total number of items available for return.  May not be a tight estimate for facet queries

        :param total_items: The total_items of this HistoryResponse.
        :type: int
        """

        self._total_items = total_items

    @property
    def more_items(self):
        """
        Gets the more_items of this HistoryResponse.
        Whether more items are available for return by increment offset or cursor

        :return: The more_items of this HistoryResponse.
        :rtype: bool
        """
        return self._more_items

    @more_items.setter
    def more_items(self, more_items):
        """
        Sets the more_items of this HistoryResponse.
        Whether more items are available for return by increment offset or cursor

        :param more_items: The more_items of this HistoryResponse.
        :type: bool
        """

        self._more_items = more_items

    @property
    def sort(self):
        """
        Gets the sort of this HistoryResponse.

        :return: The sort of this HistoryResponse.
        :rtype: Sorting
        """
        return self._sort

    @sort.setter
    def sort(self, sort):
        """
        Sets the sort of this HistoryResponse.

        :param sort: The sort of this HistoryResponse.
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
        if not isinstance(other, HistoryResponse):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
