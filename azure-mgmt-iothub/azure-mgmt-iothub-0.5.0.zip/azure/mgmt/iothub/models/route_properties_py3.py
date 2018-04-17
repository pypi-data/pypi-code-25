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


class RouteProperties(Model):
    """The properties of a routing rule that your IoT hub uses to route messages
    to endpoints.

    All required parameters must be populated in order to send to Azure.

    :param name: Required. The name of the route. The name can only include
     alphanumeric characters, periods, underscores, hyphens, has a maximum
     length of 64 characters, and must be unique.
    :type name: str
    :param source: Required. The source that the routing rule is to be applied
     to, such as DeviceMessages. Possible values include: 'DeviceMessages',
     'TwinChangeEvents', 'DeviceLifecycleEvents', 'DeviceJobLifecycleEvents'
    :type source: str or ~azure.mgmt.iothub.models.RoutingSource
    :param condition: The condition that is evaluated to apply the routing
     rule. If no condition is provided, it evaluates to true by default. For
     grammar, see:
     https://docs.microsoft.com/azure/iot-hub/iot-hub-devguide-query-language
    :type condition: str
    :param endpoint_names: Required. The list of endpoints to which messages
     that satisfy the condition are routed. Currently only one endpoint is
     allowed.
    :type endpoint_names: list[str]
    :param is_enabled: Required. Used to specify whether a route is enabled.
    :type is_enabled: bool
    """

    _validation = {
        'name': {'required': True, 'pattern': r'^[A-Za-z0-9-._]{1,64}$'},
        'source': {'required': True},
        'endpoint_names': {'required': True, 'max_items': 1, 'min_items': 1},
        'is_enabled': {'required': True},
    }

    _attribute_map = {
        'name': {'key': 'name', 'type': 'str'},
        'source': {'key': 'source', 'type': 'str'},
        'condition': {'key': 'condition', 'type': 'str'},
        'endpoint_names': {'key': 'endpointNames', 'type': '[str]'},
        'is_enabled': {'key': 'isEnabled', 'type': 'bool'},
    }

    def __init__(self, *, name: str, source, endpoint_names, is_enabled: bool, condition: str=None, **kwargs) -> None:
        super(RouteProperties, self).__init__(**kwargs)
        self.name = name
        self.source = source
        self.condition = condition
        self.endpoint_names = endpoint_names
        self.is_enabled = is_enabled
