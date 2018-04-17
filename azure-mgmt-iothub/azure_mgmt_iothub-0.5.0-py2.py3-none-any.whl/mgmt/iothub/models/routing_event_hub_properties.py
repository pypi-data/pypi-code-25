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


class RoutingEventHubProperties(Model):
    """The properties related to an event hub endpoint.

    All required parameters must be populated in order to send to Azure.

    :param connection_string: Required. The connection string of the event hub
     endpoint.
    :type connection_string: str
    :param name: Required. The name that identifies this endpoint. The name
     can only include alphanumeric characters, periods, underscores, hyphens
     and has a maximum length of 64 characters. The following names are
     reserved:  events, operationsMonitoringEvents, fileNotifications,
     $default. Endpoint names must be unique across endpoint types.
    :type name: str
    :param subscription_id: The subscription identifier of the event hub
     endpoint.
    :type subscription_id: str
    :param resource_group: The name of the resource group of the event hub
     endpoint.
    :type resource_group: str
    """

    _validation = {
        'connection_string': {'required': True},
        'name': {'required': True, 'pattern': r'^[A-Za-z0-9-._]{1,64}$'},
    }

    _attribute_map = {
        'connection_string': {'key': 'connectionString', 'type': 'str'},
        'name': {'key': 'name', 'type': 'str'},
        'subscription_id': {'key': 'subscriptionId', 'type': 'str'},
        'resource_group': {'key': 'resourceGroup', 'type': 'str'},
    }

    def __init__(self, **kwargs):
        super(RoutingEventHubProperties, self).__init__(**kwargs)
        self.connection_string = kwargs.get('connection_string', None)
        self.name = kwargs.get('name', None)
        self.subscription_id = kwargs.get('subscription_id', None)
        self.resource_group = kwargs.get('resource_group', None)
