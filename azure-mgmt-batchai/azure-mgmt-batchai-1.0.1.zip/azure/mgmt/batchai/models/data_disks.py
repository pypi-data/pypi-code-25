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


class DataDisks(Model):
    """Settings for the data disk which would be created for the File Server.

    All required parameters must be populated in order to send to Azure.

    :param disk_size_in_gb: Required. Initial disk size in GB for blank data
     disks, and the new desired size for resizing existing data disks.
    :type disk_size_in_gb: int
    :param caching_type: None, ReadOnly, ReadWrite. Default value is None.
     This property is not patchable. Possible values include: 'none',
     'readonly', 'readwrite'. Default value: "none" .
    :type caching_type: str or ~azure.mgmt.batchai.models.CachingType
    :param disk_count: Required. Number of data disks to be attached to the
     VM. RAID level 0 will be applied in the case of multiple disks.
    :type disk_count: int
    :param storage_account_type: Required. Specifies the type of storage
     account to be used on the disk. Possible values are: Standard_LRS or
     Premium_LRS. Possible values include: 'Standard_LRS', 'Premium_LRS'
    :type storage_account_type: str or
     ~azure.mgmt.batchai.models.StorageAccountType
    """

    _validation = {
        'disk_size_in_gb': {'required': True},
        'disk_count': {'required': True},
        'storage_account_type': {'required': True},
    }

    _attribute_map = {
        'disk_size_in_gb': {'key': 'diskSizeInGB', 'type': 'int'},
        'caching_type': {'key': 'cachingType', 'type': 'CachingType'},
        'disk_count': {'key': 'diskCount', 'type': 'int'},
        'storage_account_type': {'key': 'storageAccountType', 'type': 'str'},
    }

    def __init__(self, **kwargs):
        super(DataDisks, self).__init__(**kwargs)
        self.disk_size_in_gb = kwargs.get('disk_size_in_gb', None)
        self.caching_type = kwargs.get('caching_type', "none")
        self.disk_count = kwargs.get('disk_count', None)
        self.storage_account_type = kwargs.get('storage_account_type', None)
