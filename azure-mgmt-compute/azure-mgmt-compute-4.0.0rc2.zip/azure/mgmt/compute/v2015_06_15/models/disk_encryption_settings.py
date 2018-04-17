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


class DiskEncryptionSettings(Model):
    """Describes a Encryption Settings for a Disk.

    All required parameters must be populated in order to send to Azure.

    :param disk_encryption_key: Required. Specifies the location of the disk
     encryption key, which is a Key Vault Secret.
    :type disk_encryption_key:
     ~azure.mgmt.compute.v2015_06_15.models.KeyVaultSecretReference
    :param key_encryption_key: Specifies the location of the key encryption
     key in Key Vault.
    :type key_encryption_key:
     ~azure.mgmt.compute.v2015_06_15.models.KeyVaultKeyReference
    :param enabled: Specifies whether disk encryption should be enabled on the
     virtual machine.
    :type enabled: bool
    """

    _validation = {
        'disk_encryption_key': {'required': True},
    }

    _attribute_map = {
        'disk_encryption_key': {'key': 'diskEncryptionKey', 'type': 'KeyVaultSecretReference'},
        'key_encryption_key': {'key': 'keyEncryptionKey', 'type': 'KeyVaultKeyReference'},
        'enabled': {'key': 'enabled', 'type': 'bool'},
    }

    def __init__(self, **kwargs):
        super(DiskEncryptionSettings, self).__init__(**kwargs)
        self.disk_encryption_key = kwargs.get('disk_encryption_key', None)
        self.key_encryption_key = kwargs.get('key_encryption_key', None)
        self.enabled = kwargs.get('enabled', None)
