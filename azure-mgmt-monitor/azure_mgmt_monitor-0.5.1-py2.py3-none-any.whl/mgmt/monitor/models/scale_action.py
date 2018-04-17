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


class ScaleAction(Model):
    """The parameters for the scaling action.

    All required parameters must be populated in order to send to Azure.

    :param direction: Required. the scale direction. Whether the scaling
     action increases or decreases the number of instances. Possible values
     include: 'None', 'Increase', 'Decrease'
    :type direction: str or ~azure.mgmt.monitor.models.ScaleDirection
    :param type: Required. the type of action that should occur when the scale
     rule fires. Possible values include: 'ChangeCount', 'PercentChangeCount',
     'ExactCount'
    :type type: str or ~azure.mgmt.monitor.models.ScaleType
    :param value: the number of instances that are involved in the scaling
     action. This value must be 1 or greater. The default value is 1. Default
     value: "1" .
    :type value: str
    :param cooldown: Required. the amount of time to wait since the last
     scaling action before this action occurs. It must be between 1 week and 1
     minute in ISO 8601 format.
    :type cooldown: timedelta
    """

    _validation = {
        'direction': {'required': True},
        'type': {'required': True},
        'cooldown': {'required': True},
    }

    _attribute_map = {
        'direction': {'key': 'direction', 'type': 'ScaleDirection'},
        'type': {'key': 'type', 'type': 'ScaleType'},
        'value': {'key': 'value', 'type': 'str'},
        'cooldown': {'key': 'cooldown', 'type': 'duration'},
    }

    def __init__(self, **kwargs):
        super(ScaleAction, self).__init__(**kwargs)
        self.direction = kwargs.get('direction', None)
        self.type = kwargs.get('type', None)
        self.value = kwargs.get('value', "1")
        self.cooldown = kwargs.get('cooldown', None)
