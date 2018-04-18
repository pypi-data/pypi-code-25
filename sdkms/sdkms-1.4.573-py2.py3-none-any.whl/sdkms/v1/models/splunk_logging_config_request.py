# coding: utf-8

"""
    Fortanix SDKMS REST API

    This is a set of REST APIs for accessing the Fortanix Self-Defending Key Management System. This includes APIs for managing accounts, and for performing cryptographic and key management operations. 

    OpenAPI spec version: 1.0.0-20171218
    Contact: support@fortanix.com
    Generated by: https://github.com/swagger-api/swagger-codegen.git

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
    
        http://www.apache.org/licenses/LICENSE-2.0
    
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""


from pprint import pformat
from six import iteritems
import re




# NOTE: This class is auto generated by the swagger code generator program.
# Do not edit the class manually.
class SplunkLoggingConfigRequest(object):
    """
    @undocumented: swagger_types
    @undocumented: attribute_map
    @undocumented: to_dict
    @undocumented: to_str
    @undocumented: __repr__
    @undocumented: __eq__
    @undocumented: __ne__
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'host': 'str',
        'port': 'int',
        'index': 'str',
        'token': 'str',
        'tls': 'TlsConfig',
        'enabled': 'bool'
    }

    attribute_map = {
        'host': 'host',
        'port': 'port',
        'index': 'index',
        'token': 'token',
        'tls': 'tls',
        'enabled': 'enabled'
    }

    def __init__(self, host=None, port=None, index=None, token=None, tls=None, enabled=None):
        """
        SplunkLoggingConfigRequest - a model defined in Swagger
        """

        self._host = None
        self._port = None
        self._index = None
        self._token = None
        self._tls = None
        self._enabled = None

        if host is not None:
          self.host = host
        if port is not None:
          self.port = port
        if index is not None:
          self.index = index
        if token is not None:
          self.token = token
        if tls is not None:
          self.tls = tls
        if enabled is not None:
          self.enabled = enabled

    @property
    def host(self):
        """
        Gets the host of this SplunkLoggingConfigRequest.

        Type: L{str}
        """
        return self._host

    @host.setter
    def host(self, host):
        """
        Sets the host of this SplunkLoggingConfigRequest.
        """

        self._host = host

    @property
    def port(self):
        """
        Gets the port of this SplunkLoggingConfigRequest.

        Type: L{int}
        """
        return self._port

    @port.setter
    def port(self, port):
        """
        Sets the port of this SplunkLoggingConfigRequest.
        """

        self._port = port

    @property
    def index(self):
        """
        Gets the index of this SplunkLoggingConfigRequest.
        The Splunk index that will receive log items

        Type: L{str}
        """
        return self._index

    @index.setter
    def index(self, index):
        """
        Sets the index of this SplunkLoggingConfigRequest.
        The Splunk index that will receive log items
        """

        self._index = index

    @property
    def token(self):
        """
        Gets the token of this SplunkLoggingConfigRequest.
        The Splunk authentication token

        Type: L{str}
        """
        return self._token

    @token.setter
    def token(self, token):
        """
        Sets the token of this SplunkLoggingConfigRequest.
        The Splunk authentication token
        """

        self._token = token

    @property
    def tls(self):
        """
        Gets the tls of this SplunkLoggingConfigRequest.

        Type: L{TlsConfig}
        """
        return self._tls

    @tls.setter
    def tls(self, tls):
        """
        Sets the tls of this SplunkLoggingConfigRequest.
        """

        self._tls = tls

    @property
    def enabled(self):
        """
        Gets the enabled of this SplunkLoggingConfigRequest.

        Type: L{bool}
        """
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        """
        Sets the enabled of this SplunkLoggingConfigRequest.
        """

        self._enabled = enabled

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
        if not isinstance(other, SplunkLoggingConfigRequest):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other

