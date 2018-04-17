# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class CloudToDeviceProperties(Model):
    """The IoT hub cloud-to-device messaging properties.

    :param max_delivery_count: The max delivery count for cloud-to-device
     messages in the device queue. See:
     https://docs.microsoft.com/azure/iot-hub/iot-hub-devguide-messaging#cloud-to-device-messages.
    :type max_delivery_count: int
    :param default_ttl_as_iso8601: The default time to live for
     cloud-to-device messages in the device queue. See:
     https://docs.microsoft.com/azure/iot-hub/iot-hub-devguide-messaging#cloud-to-device-messages.
    :type default_ttl_as_iso8601: timedelta
    :param feedback:
    :type feedback: ~azure.mgmt.iothub.models.FeedbackProperties
    """

    _validation = {
        'max_delivery_count': {'maximum': 100, 'minimum': 1},
    }

    _attribute_map = {
        'max_delivery_count': {'key': 'maxDeliveryCount', 'type': 'int'},
        'default_ttl_as_iso8601': {'key': 'defaultTtlAsIso8601', 'type': 'duration'},
        'feedback': {'key': 'feedback', 'type': 'FeedbackProperties'},
    }

    def __init__(self, *, max_delivery_count: int=None, default_ttl_as_iso8601=None, feedback=None, **kwargs) -> None:
        super(CloudToDeviceProperties, self).__init__(**kwargs)
        self.max_delivery_count = max_delivery_count
        self.default_ttl_as_iso8601 = default_ttl_as_iso8601
        self.feedback = feedback
