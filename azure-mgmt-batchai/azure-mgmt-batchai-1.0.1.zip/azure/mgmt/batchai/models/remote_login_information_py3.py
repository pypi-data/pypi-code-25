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


class RemoteLoginInformation(Model):
    """Contains remote login details to SSH/RDP to a compute node in cluster.

    All required parameters must be populated in order to send to Azure.

    :param node_id: Required. Id of the compute node
    :type node_id: str
    :param ip_address: Required. ip address
    :type ip_address: str
    :param port: Required. port number.
    :type port: float
    """

    _validation = {
        'node_id': {'required': True},
        'ip_address': {'required': True},
        'port': {'required': True},
    }

    _attribute_map = {
        'node_id': {'key': 'nodeId', 'type': 'str'},
        'ip_address': {'key': 'ipAddress', 'type': 'str'},
        'port': {'key': 'port', 'type': 'float'},
    }

    def __init__(self, *, node_id: str, ip_address: str, port: float, **kwargs) -> None:
        super(RemoteLoginInformation, self).__init__(**kwargs)
        self.node_id = node_id
        self.ip_address = ip_address
        self.port = port
