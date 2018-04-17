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

from .sub_resource_read_only import SubResourceReadOnly


class VirtualMachineScaleSetExtension(SubResourceReadOnly):
    """Describes a Virtual Machine Scale Set Extension.

    Variables are only populated by the server, and will be ignored when
    sending a request.

    :ivar id: Resource Id
    :vartype id: str
    :param name: The name of the extension.
    :type name: str
    :param force_update_tag: If a value is provided and is different from the
     previous value, the extension handler will be forced to update even if the
     extension configuration has not changed.
    :type force_update_tag: str
    :param publisher: The name of the extension handler publisher.
    :type publisher: str
    :param type: Specifies the type of the extension; an example is
     "CustomScriptExtension".
    :type type: str
    :param type_handler_version: Specifies the version of the script handler.
    :type type_handler_version: str
    :param auto_upgrade_minor_version: Indicates whether the extension should
     use a newer minor version if one is available at deployment time. Once
     deployed, however, the extension will not upgrade minor versions unless
     redeployed, even with this property set to true.
    :type auto_upgrade_minor_version: bool
    :param settings: Json formatted public settings for the extension.
    :type settings: object
    :param protected_settings: The extension can contain either
     protectedSettings or protectedSettingsFromKeyVault or no protected
     settings at all.
    :type protected_settings: object
    :ivar provisioning_state: The provisioning state, which only appears in
     the response.
    :vartype provisioning_state: str
    """

    _validation = {
        'id': {'readonly': True},
        'provisioning_state': {'readonly': True},
    }

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'name': {'key': 'name', 'type': 'str'},
        'force_update_tag': {'key': 'properties.forceUpdateTag', 'type': 'str'},
        'publisher': {'key': 'properties.publisher', 'type': 'str'},
        'type': {'key': 'properties.type', 'type': 'str'},
        'type_handler_version': {'key': 'properties.typeHandlerVersion', 'type': 'str'},
        'auto_upgrade_minor_version': {'key': 'properties.autoUpgradeMinorVersion', 'type': 'bool'},
        'settings': {'key': 'properties.settings', 'type': 'object'},
        'protected_settings': {'key': 'properties.protectedSettings', 'type': 'object'},
        'provisioning_state': {'key': 'properties.provisioningState', 'type': 'str'},
    }

    def __init__(self, *, name: str=None, force_update_tag: str=None, publisher: str=None, type: str=None, type_handler_version: str=None, auto_upgrade_minor_version: bool=None, settings=None, protected_settings=None, **kwargs) -> None:
        super(VirtualMachineScaleSetExtension, self).__init__(**kwargs)
        self.name = name
        self.force_update_tag = force_update_tag
        self.publisher = publisher
        self.type = type
        self.type_handler_version = type_handler_version
        self.auto_upgrade_minor_version = auto_upgrade_minor_version
        self.settings = settings
        self.protected_settings = protected_settings
        self.provisioning_state = None
