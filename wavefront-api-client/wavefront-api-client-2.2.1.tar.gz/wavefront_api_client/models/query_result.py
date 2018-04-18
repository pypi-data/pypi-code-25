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


class QueryResult(object):
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
        'name': 'str',
        'query': 'str',
        'warnings': 'str',
        'stats': 'StatsModel',
        'granularity': 'int',
        'timeseries': 'list[Timeseries]',
        'events': 'list[QueryEvent]'
    }

    attribute_map = {
        'name': 'name',
        'query': 'query',
        'warnings': 'warnings',
        'stats': 'stats',
        'granularity': 'granularity',
        'timeseries': 'timeseries',
        'events': 'events'
    }

    def __init__(self, name=None, query=None, warnings=None, stats=None, granularity=None, timeseries=None, events=None):
        """
        QueryResult - a model defined in Swagger
        """

        self._name = None
        self._query = None
        self._warnings = None
        self._stats = None
        self._granularity = None
        self._timeseries = None
        self._events = None
        self.discriminator = None

        if name is not None:
          self.name = name
        if query is not None:
          self.query = query
        if warnings is not None:
          self.warnings = warnings
        if stats is not None:
          self.stats = stats
        if granularity is not None:
          self.granularity = granularity
        if timeseries is not None:
          self.timeseries = timeseries
        if events is not None:
          self.events = events

    @property
    def name(self):
        """
        Gets the name of this QueryResult.
        The name of this query

        :return: The name of this QueryResult.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this QueryResult.
        The name of this query

        :param name: The name of this QueryResult.
        :type: str
        """

        self._name = name

    @property
    def query(self):
        """
        Gets the query of this QueryResult.
        The query used to obtain this result

        :return: The query of this QueryResult.
        :rtype: str
        """
        return self._query

    @query.setter
    def query(self, query):
        """
        Sets the query of this QueryResult.
        The query used to obtain this result

        :param query: The query of this QueryResult.
        :type: str
        """

        self._query = query

    @property
    def warnings(self):
        """
        Gets the warnings of this QueryResult.
        The warnings incurred by this query

        :return: The warnings of this QueryResult.
        :rtype: str
        """
        return self._warnings

    @warnings.setter
    def warnings(self, warnings):
        """
        Sets the warnings of this QueryResult.
        The warnings incurred by this query

        :param warnings: The warnings of this QueryResult.
        :type: str
        """

        self._warnings = warnings

    @property
    def stats(self):
        """
        Gets the stats of this QueryResult.

        :return: The stats of this QueryResult.
        :rtype: StatsModel
        """
        return self._stats

    @stats.setter
    def stats(self, stats):
        """
        Sets the stats of this QueryResult.

        :param stats: The stats of this QueryResult.
        :type: StatsModel
        """

        self._stats = stats

    @property
    def granularity(self):
        """
        Gets the granularity of this QueryResult.
        The granularity of the returned results, in seconds

        :return: The granularity of this QueryResult.
        :rtype: int
        """
        return self._granularity

    @granularity.setter
    def granularity(self, granularity):
        """
        Sets the granularity of this QueryResult.
        The granularity of the returned results, in seconds

        :param granularity: The granularity of this QueryResult.
        :type: int
        """

        self._granularity = granularity

    @property
    def timeseries(self):
        """
        Gets the timeseries of this QueryResult.

        :return: The timeseries of this QueryResult.
        :rtype: list[Timeseries]
        """
        return self._timeseries

    @timeseries.setter
    def timeseries(self, timeseries):
        """
        Sets the timeseries of this QueryResult.

        :param timeseries: The timeseries of this QueryResult.
        :type: list[Timeseries]
        """

        self._timeseries = timeseries

    @property
    def events(self):
        """
        Gets the events of this QueryResult.

        :return: The events of this QueryResult.
        :rtype: list[QueryEvent]
        """
        return self._events

    @events.setter
    def events(self, events):
        """
        Sets the events of this QueryResult.

        :param events: The events of this QueryResult.
        :type: list[QueryEvent]
        """

        self._events = events

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
        if not isinstance(other, QueryResult):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
