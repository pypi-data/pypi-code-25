# coding: utf-8

"""
Copyright 2016 SmartBear Software

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Ref: https://github.com/swagger-api/swagger-codegen
"""

from pprint import pformat
from six import iteritems


class MaintenanceWindow(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self):
        """
        MaintenanceWindow - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'created_at': 'int',
            'creator_user_id': 'str',
            'customer_id': 'str',
            'end_time_in_seconds': 'int',
            'event_name': 'str',
            'reason': 'str',
            'relevant_customer_tags': 'list[str]',
            'relevant_host_names': 'list[str]',
            'relevant_host_tags': 'list[str]',
            'start_time_in_seconds': 'int',
            'title': 'str'
        }

        self.attribute_map = {
            'created_at': 'createdAt',
            'creator_user_id': 'creatorUserId',
            'customer_id': 'customerId',
            'end_time_in_seconds': 'endTimeInSeconds',
            'event_name': 'eventName',
            'reason': 'reason',
            'relevant_customer_tags': 'relevantCustomerTags',
            'relevant_host_names': 'relevantHostNames',
            'relevant_host_tags': 'relevantHostTags',
            'start_time_in_seconds': 'startTimeInSeconds',
            'title': 'title'
        }

        self._created_at = None
        self._creator_user_id = None
        self._customer_id = None
        self._end_time_in_seconds = None
        self._event_name = None
        self._reason = None
        self._relevant_customer_tags = None
        self._relevant_host_names = None
        self._relevant_host_tags = None
        self._start_time_in_seconds = None
        self._title = None

    @property
    def created_at(self):
        """
        Gets the created_at of this MaintenanceWindow.
        The creation time for this maintenance window in milliseconds. Used as the id

        :return: The created_at of this MaintenanceWindow.
        :rtype: int
        """
        return self._created_at

    @created_at.setter
    def created_at(self, created_at):
        """
        Sets the created_at of this MaintenanceWindow.
        The creation time for this maintenance window in milliseconds. Used as the id

        :param created_at: The created_at of this MaintenanceWindow.
        :type: int
        """
        self._created_at = created_at

    @property
    def creator_user_id(self):
        """
        Gets the creator_user_id of this MaintenanceWindow.
        Id of the user who created this maintenance window

        :return: The creator_user_id of this MaintenanceWindow.
        :rtype: str
        """
        return self._creator_user_id

    @creator_user_id.setter
    def creator_user_id(self, creator_user_id):
        """
        Sets the creator_user_id of this MaintenanceWindow.
        Id of the user who created this maintenance window

        :param creator_user_id: The creator_user_id of this MaintenanceWindow.
        :type: str
        """
        self._creator_user_id = creator_user_id

    @property
    def customer_id(self):
        """
        Gets the customer_id of this MaintenanceWindow.


        :return: The customer_id of this MaintenanceWindow.
        :rtype: str
        """
        return self._customer_id

    @customer_id.setter
    def customer_id(self, customer_id):
        """
        Sets the customer_id of this MaintenanceWindow.


        :param customer_id: The customer_id of this MaintenanceWindow.
        :type: str
        """
        self._customer_id = customer_id

    @property
    def end_time_in_seconds(self):
        """
        Gets the end_time_in_seconds of this MaintenanceWindow.
        The time in seconds for when this maintenance window will end

        :return: The end_time_in_seconds of this MaintenanceWindow.
        :rtype: int
        """
        return self._end_time_in_seconds

    @end_time_in_seconds.setter
    def end_time_in_seconds(self, end_time_in_seconds):
        """
        Sets the end_time_in_seconds of this MaintenanceWindow.
        The time in seconds for when this maintenance window will end

        :param end_time_in_seconds: The end_time_in_seconds of this MaintenanceWindow.
        :type: int
        """
        self._end_time_in_seconds = end_time_in_seconds

    @property
    def event_name(self):
        """
        Gets the event_name of this MaintenanceWindow.


        :return: The event_name of this MaintenanceWindow.
        :rtype: str
        """
        return self._event_name

    @event_name.setter
    def event_name(self, event_name):
        """
        Sets the event_name of this MaintenanceWindow.


        :param event_name: The event_name of this MaintenanceWindow.
        :type: str
        """
        self._event_name = event_name

    @property
    def reason(self):
        """
        Gets the reason of this MaintenanceWindow.
        Description on the purpose of this maintenance window

        :return: The reason of this MaintenanceWindow.
        :rtype: str
        """
        return self._reason

    @reason.setter
    def reason(self, reason):
        """
        Sets the reason of this MaintenanceWindow.
        Description on the purpose of this maintenance window

        :param reason: The reason of this MaintenanceWindow.
        :type: str
        """
        self._reason = reason

    @property
    def relevant_customer_tags(self):
        """
        Gets the relevant_customer_tags of this MaintenanceWindow.
        List of shared alert tags that will be put into maintenance because of this maintenance window

        :return: The relevant_customer_tags of this MaintenanceWindow.
        :rtype: list[str]
        """
        return self._relevant_customer_tags

    @relevant_customer_tags.setter
    def relevant_customer_tags(self, relevant_customer_tags):
        """
        Sets the relevant_customer_tags of this MaintenanceWindow.
        List of shared alert tags that will be put into maintenance because of this maintenance window

        :param relevant_customer_tags: The relevant_customer_tags of this MaintenanceWindow.
        :type: list[str]
        """
        self._relevant_customer_tags = relevant_customer_tags

    @property
    def relevant_host_names(self):
        """
        Gets the relevant_host_names of this MaintenanceWindow.
        List of the specific hosts that will be put into maintenance because of this maintenance window

        :return: The relevant_host_names of this MaintenanceWindow.
        :rtype: list[str]
        """
        return self._relevant_host_names

    @relevant_host_names.setter
    def relevant_host_names(self, relevant_host_names):
        """
        Sets the relevant_host_names of this MaintenanceWindow.
        List of the specific hosts that will be put into maintenance because of this maintenance window

        :param relevant_host_names: The relevant_host_names of this MaintenanceWindow.
        :type: list[str]
        """
        self._relevant_host_names = relevant_host_names

    @property
    def relevant_host_tags(self):
        """
        Gets the relevant_host_tags of this MaintenanceWindow.
        List of host tags whose matching hosts will be put into maintenance because of this maintenance window

        :return: The relevant_host_tags of this MaintenanceWindow.
        :rtype: list[str]
        """
        return self._relevant_host_tags

    @relevant_host_tags.setter
    def relevant_host_tags(self, relevant_host_tags):
        """
        Sets the relevant_host_tags of this MaintenanceWindow.
        List of host tags whose matching hosts will be put into maintenance because of this maintenance window

        :param relevant_host_tags: The relevant_host_tags of this MaintenanceWindow.
        :type: list[str]
        """
        self._relevant_host_tags = relevant_host_tags

    @property
    def start_time_in_seconds(self):
        """
        Gets the start_time_in_seconds of this MaintenanceWindow.
        The time in seconds for when this maintenance window will start

        :return: The start_time_in_seconds of this MaintenanceWindow.
        :rtype: int
        """
        return self._start_time_in_seconds

    @start_time_in_seconds.setter
    def start_time_in_seconds(self, start_time_in_seconds):
        """
        Sets the start_time_in_seconds of this MaintenanceWindow.
        The time in seconds for when this maintenance window will start

        :param start_time_in_seconds: The start_time_in_seconds of this MaintenanceWindow.
        :type: int
        """
        self._start_time_in_seconds = start_time_in_seconds

    @property
    def title(self):
        """
        Gets the title of this MaintenanceWindow.
        Title text

        :return: The title of this MaintenanceWindow.
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """
        Sets the title of this MaintenanceWindow.
        Title text

        :param title: The title of this MaintenanceWindow.
        :type: str
        """
        self._title = title

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
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other

