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


class PagedWebhook(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, items=None, offset=None, limit=None, cursor=None, total_items=None, more_items=None, sort=None):
        """
        PagedWebhook - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'items': 'list[Webhook]',
            'offset': 'int',
            'limit': 'int',
            'cursor': 'str',
            'total_items': 'int',
            'more_items': 'bool',
            'sort': 'Sorting'
        }

        self.attribute_map = {
            'items': 'items',
            'offset': 'offset',
            'limit': 'limit',
            'cursor': 'cursor',
            'total_items': 'totalItems',
            'more_items': 'moreItems',
            'sort': 'sort'
        }

        self._items = items
        self._offset = offset
        self._limit = limit
        self._cursor = cursor
        self._total_items = total_items
        self._more_items = more_items
        self._sort = sort

    @property
    def items(self):
        """
        Gets the items of this PagedWebhook.
        List of requested items

        :return: The items of this PagedWebhook.
        :rtype: list[Webhook]
        """
        return self._items

    @items.setter
    def items(self, items):
        """
        Sets the items of this PagedWebhook.
        List of requested items

        :param items: The items of this PagedWebhook.
        :type: list[Webhook]
        """

        self._items = items

    @property
    def offset(self):
        """
        Gets the offset of this PagedWebhook.

        :return: The offset of this PagedWebhook.
        :rtype: int
        """
        return self._offset

    @offset.setter
    def offset(self, offset):
        """
        Sets the offset of this PagedWebhook.

        :param offset: The offset of this PagedWebhook.
        :type: int
        """

        self._offset = offset

    @property
    def limit(self):
        """
        Gets the limit of this PagedWebhook.

        :return: The limit of this PagedWebhook.
        :rtype: int
        """
        return self._limit

    @limit.setter
    def limit(self, limit):
        """
        Sets the limit of this PagedWebhook.

        :param limit: The limit of this PagedWebhook.
        :type: int
        """

        self._limit = limit

    @property
    def cursor(self):
        """
        Gets the cursor of this PagedWebhook.
        The id at which the current (limited) search can be continued to obtain more matching items

        :return: The cursor of this PagedWebhook.
        :rtype: str
        """
        return self._cursor

    @cursor.setter
    def cursor(self, cursor):
        """
        Sets the cursor of this PagedWebhook.
        The id at which the current (limited) search can be continued to obtain more matching items

        :param cursor: The cursor of this PagedWebhook.
        :type: str
        """

        self._cursor = cursor

    @property
    def total_items(self):
        """
        Gets the total_items of this PagedWebhook.
        An estimate (lower-bound) of the total number of items available for return.  May not be a tight estimate for facet queries

        :return: The total_items of this PagedWebhook.
        :rtype: int
        """
        return self._total_items

    @total_items.setter
    def total_items(self, total_items):
        """
        Sets the total_items of this PagedWebhook.
        An estimate (lower-bound) of the total number of items available for return.  May not be a tight estimate for facet queries

        :param total_items: The total_items of this PagedWebhook.
        :type: int
        """

        self._total_items = total_items

    @property
    def more_items(self):
        """
        Gets the more_items of this PagedWebhook.
        Whether more items are available for return by increment offset or cursor

        :return: The more_items of this PagedWebhook.
        :rtype: bool
        """
        return self._more_items

    @more_items.setter
    def more_items(self, more_items):
        """
        Sets the more_items of this PagedWebhook.
        Whether more items are available for return by increment offset or cursor

        :param more_items: The more_items of this PagedWebhook.
        :type: bool
        """

        self._more_items = more_items

    @property
    def sort(self):
        """
        Gets the sort of this PagedWebhook.
        How returned items have been sorted

        :return: The sort of this PagedWebhook.
        :rtype: Sorting
        """
        return self._sort

    @sort.setter
    def sort(self, sort):
        """
        Sets the sort of this PagedWebhook.
        How returned items have been sorted

        :param sort: The sort of this PagedWebhook.
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
        if not isinstance(other, PagedWebhook):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
