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


class VirtualMachineScaleSetPublicIPAddressConfiguration(Model):
    """Describes a virtual machines scale set IP Configuration's PublicIPAddress
    configuration.

    All required parameters must be populated in order to send to Azure.

    :param name: Required. The publicIP address configuration name.
    :type name: str
    :param idle_timeout_in_minutes: The idle timeout of the public IP address.
    :type idle_timeout_in_minutes: int
    :param dns_settings: The dns settings to be applied on the publicIP
     addresses .
    :type dns_settings:
     ~azure.mgmt.compute.v2017_12_01.models.VirtualMachineScaleSetPublicIPAddressConfigurationDnsSettings
    """

    _validation = {
        'name': {'required': True},
    }

    _attribute_map = {
        'name': {'key': 'name', 'type': 'str'},
        'idle_timeout_in_minutes': {'key': 'properties.idleTimeoutInMinutes', 'type': 'int'},
        'dns_settings': {'key': 'properties.dnsSettings', 'type': 'VirtualMachineScaleSetPublicIPAddressConfigurationDnsSettings'},
    }

    def __init__(self, **kwargs):
        super(VirtualMachineScaleSetPublicIPAddressConfiguration, self).__init__(**kwargs)
        self.name = kwargs.get('name', None)
        self.idle_timeout_in_minutes = kwargs.get('idle_timeout_in_minutes', None)
        self.dns_settings = kwargs.get('dns_settings', None)
