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


class Message(object):
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
        'scope': 'str',
        'source': 'str',
        'attributes': 'dict(str, str)',
        'id': 'str',
        'target': 'str',
        'content': 'str',
        'title': 'str',
        'severity': 'str',
        'start_epoch_millis': 'int',
        'end_epoch_millis': 'int',
        'display': 'str',
        'read': 'bool'
    }

    attribute_map = {
        'scope': 'scope',
        'source': 'source',
        'attributes': 'attributes',
        'id': 'id',
        'target': 'target',
        'content': 'content',
        'title': 'title',
        'severity': 'severity',
        'start_epoch_millis': 'startEpochMillis',
        'end_epoch_millis': 'endEpochMillis',
        'display': 'display',
        'read': 'read'
    }

    def __init__(self, scope=None, source=None, attributes=None, id=None, target=None, content=None, title=None, severity=None, start_epoch_millis=None, end_epoch_millis=None, display=None, read=None):
        """
        Message - a model defined in Swagger
        """

        self._scope = None
        self._source = None
        self._attributes = None
        self._id = None
        self._target = None
        self._content = None
        self._title = None
        self._severity = None
        self._start_epoch_millis = None
        self._end_epoch_millis = None
        self._display = None
        self._read = None
        self.discriminator = None

        self.scope = scope
        self.source = source
        if attributes is not None:
          self.attributes = attributes
        if id is not None:
          self.id = id
        if target is not None:
          self.target = target
        self.content = content
        self.title = title
        self.severity = severity
        self.start_epoch_millis = start_epoch_millis
        self.end_epoch_millis = end_epoch_millis
        self.display = display
        if read is not None:
          self.read = read

    @property
    def scope(self):
        """
        Gets the scope of this Message.
        The audience scope that this message should reach

        :return: The scope of this Message.
        :rtype: str
        """
        return self._scope

    @scope.setter
    def scope(self, scope):
        """
        Sets the scope of this Message.
        The audience scope that this message should reach

        :param scope: The scope of this Message.
        :type: str
        """
        if scope is None:
            raise ValueError("Invalid value for `scope`, must not be `None`")
        allowed_values = ["CLUSTER", "CUSTOMER", "USER"]
        if scope not in allowed_values:
            raise ValueError(
                "Invalid value for `scope` ({0}), must be one of {1}"
                .format(scope, allowed_values)
            )

        self._scope = scope

    @property
    def source(self):
        """
        Gets the source of this Message.
        Message source.  System messages will com from 'system@wavefront.com'

        :return: The source of this Message.
        :rtype: str
        """
        return self._source

    @source.setter
    def source(self, source):
        """
        Sets the source of this Message.
        Message source.  System messages will com from 'system@wavefront.com'

        :param source: The source of this Message.
        :type: str
        """
        if source is None:
            raise ValueError("Invalid value for `source`, must not be `None`")

        self._source = source

    @property
    def attributes(self):
        """
        Gets the attributes of this Message.
        A string->string map of additional properties associated with this message

        :return: The attributes of this Message.
        :rtype: dict(str, str)
        """
        return self._attributes

    @attributes.setter
    def attributes(self, attributes):
        """
        Sets the attributes of this Message.
        A string->string map of additional properties associated with this message

        :param attributes: The attributes of this Message.
        :type: dict(str, str)
        """

        self._attributes = attributes

    @property
    def id(self):
        """
        Gets the id of this Message.

        :return: The id of this Message.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this Message.

        :param id: The id of this Message.
        :type: str
        """

        self._id = id

    @property
    def target(self):
        """
        Gets the target of this Message.
        For scope=CUSTOMER or scope=USER, the individual customer or user id

        :return: The target of this Message.
        :rtype: str
        """
        return self._target

    @target.setter
    def target(self, target):
        """
        Sets the target of this Message.
        For scope=CUSTOMER or scope=USER, the individual customer or user id

        :param target: The target of this Message.
        :type: str
        """

        self._target = target

    @property
    def content(self):
        """
        Gets the content of this Message.
        Message content

        :return: The content of this Message.
        :rtype: str
        """
        return self._content

    @content.setter
    def content(self, content):
        """
        Sets the content of this Message.
        Message content

        :param content: The content of this Message.
        :type: str
        """
        if content is None:
            raise ValueError("Invalid value for `content`, must not be `None`")

        self._content = content

    @property
    def title(self):
        """
        Gets the title of this Message.
        Title of this message

        :return: The title of this Message.
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """
        Sets the title of this Message.
        Title of this message

        :param title: The title of this Message.
        :type: str
        """
        if title is None:
            raise ValueError("Invalid value for `title`, must not be `None`")

        self._title = title

    @property
    def severity(self):
        """
        Gets the severity of this Message.
        Message severity

        :return: The severity of this Message.
        :rtype: str
        """
        return self._severity

    @severity.setter
    def severity(self, severity):
        """
        Sets the severity of this Message.
        Message severity

        :param severity: The severity of this Message.
        :type: str
        """
        if severity is None:
            raise ValueError("Invalid value for `severity`, must not be `None`")
        allowed_values = ["MARKETING", "INFO", "WARN", "SEVERE"]
        if severity not in allowed_values:
            raise ValueError(
                "Invalid value for `severity` ({0}), must be one of {1}"
                .format(severity, allowed_values)
            )

        self._severity = severity

    @property
    def start_epoch_millis(self):
        """
        Gets the start_epoch_millis of this Message.
        When this message will begin to be displayed, in epoch millis

        :return: The start_epoch_millis of this Message.
        :rtype: int
        """
        return self._start_epoch_millis

    @start_epoch_millis.setter
    def start_epoch_millis(self, start_epoch_millis):
        """
        Sets the start_epoch_millis of this Message.
        When this message will begin to be displayed, in epoch millis

        :param start_epoch_millis: The start_epoch_millis of this Message.
        :type: int
        """
        if start_epoch_millis is None:
            raise ValueError("Invalid value for `start_epoch_millis`, must not be `None`")

        self._start_epoch_millis = start_epoch_millis

    @property
    def end_epoch_millis(self):
        """
        Gets the end_epoch_millis of this Message.
        When this message will stop being displayed, in epoch millis

        :return: The end_epoch_millis of this Message.
        :rtype: int
        """
        return self._end_epoch_millis

    @end_epoch_millis.setter
    def end_epoch_millis(self, end_epoch_millis):
        """
        Sets the end_epoch_millis of this Message.
        When this message will stop being displayed, in epoch millis

        :param end_epoch_millis: The end_epoch_millis of this Message.
        :type: int
        """
        if end_epoch_millis is None:
            raise ValueError("Invalid value for `end_epoch_millis`, must not be `None`")

        self._end_epoch_millis = end_epoch_millis

    @property
    def display(self):
        """
        Gets the display of this Message.
        The form of display for this message

        :return: The display of this Message.
        :rtype: str
        """
        return self._display

    @display.setter
    def display(self, display):
        """
        Sets the display of this Message.
        The form of display for this message

        :param display: The display of this Message.
        :type: str
        """
        if display is None:
            raise ValueError("Invalid value for `display`, must not be `None`")
        allowed_values = ["BANNER", "TOASTER"]
        if display not in allowed_values:
            raise ValueError(
                "Invalid value for `display` ({0}), must be one of {1}"
                .format(display, allowed_values)
            )

        self._display = display

    @property
    def read(self):
        """
        Gets the read of this Message.
        A derived field for whether the current user has read this message

        :return: The read of this Message.
        :rtype: bool
        """
        return self._read

    @read.setter
    def read(self, read):
        """
        Sets the read of this Message.
        A derived field for whether the current user has read this message

        :param read: The read of this Message.
        :type: bool
        """

        self._read = read

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
        if not isinstance(other, Message):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
