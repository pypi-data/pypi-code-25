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


class OSDisk(Model):
    """Specifies information about the operating system disk used by the virtual
    machine. <br><br> For more information about disks, see [About disks and
    VHDs for Azure virtual
    machines](https://docs.microsoft.com/azure/virtual-machines/virtual-machines-windows-about-disks-vhds?toc=%2fazure%2fvirtual-machines%2fwindows%2ftoc.json).

    All required parameters must be populated in order to send to Azure.

    :param os_type: This property allows you to specify the type of the OS
     that is included in the disk if creating a VM from user-image or a
     specialized VHD. <br><br> Possible values are: <br><br> **Windows**
     <br><br> **Linux**. Possible values include: 'Windows', 'Linux'
    :type os_type: str or
     ~azure.mgmt.compute.v2016_03_30.models.OperatingSystemTypes
    :param encryption_settings: Specifies the encryption settings for the OS
     Disk. <br><br> Minimum api-version: 2015-06-15
    :type encryption_settings:
     ~azure.mgmt.compute.v2016_03_30.models.DiskEncryptionSettings
    :param name: Required. The disk name.
    :type name: str
    :param vhd: Required. The virtual hard disk.
    :type vhd: ~azure.mgmt.compute.v2016_03_30.models.VirtualHardDisk
    :param image: The source user image virtual hard disk. The virtual hard
     disk will be copied before being attached to the virtual machine. If
     SourceImage is provided, the destination virtual hard drive must not
     exist.
    :type image: ~azure.mgmt.compute.v2016_03_30.models.VirtualHardDisk
    :param caching: Specifies the caching requirements. <br><br> Possible
     values are: <br><br> **None** <br><br> **ReadOnly** <br><br> **ReadWrite**
     <br><br> Default: **None for Standard storage. ReadOnly for Premium
     storage**. Possible values include: 'None', 'ReadOnly', 'ReadWrite'
    :type caching: str or ~azure.mgmt.compute.v2016_03_30.models.CachingTypes
    :param create_option: Required. Specifies how the virtual machine should
     be created.<br><br> Possible values are:<br><br> **Attach** \\u2013 This
     value is used when you are using a specialized disk to create the virtual
     machine.<br><br> **FromImage** \\u2013 This value is used when you are
     using an image to create the virtual machine. If you are using a platform
     image, you also use the imageReference element described above. If you are
     using a marketplace image, you  also use the plan element previously
     described. Possible values include: 'FromImage', 'Empty', 'Attach'
    :type create_option: str or
     ~azure.mgmt.compute.v2016_03_30.models.DiskCreateOptionTypes
    :param disk_size_gb: Specifies the size of an empty data disk in
     gigabytes. This element can be used to overwrite the name of the disk in a
     virtual machine image. <br><br> This value cannot be larger than 1023 GB
    :type disk_size_gb: int
    """

    _validation = {
        'name': {'required': True},
        'vhd': {'required': True},
        'create_option': {'required': True},
    }

    _attribute_map = {
        'os_type': {'key': 'osType', 'type': 'OperatingSystemTypes'},
        'encryption_settings': {'key': 'encryptionSettings', 'type': 'DiskEncryptionSettings'},
        'name': {'key': 'name', 'type': 'str'},
        'vhd': {'key': 'vhd', 'type': 'VirtualHardDisk'},
        'image': {'key': 'image', 'type': 'VirtualHardDisk'},
        'caching': {'key': 'caching', 'type': 'CachingTypes'},
        'create_option': {'key': 'createOption', 'type': 'DiskCreateOptionTypes'},
        'disk_size_gb': {'key': 'diskSizeGB', 'type': 'int'},
    }

    def __init__(self, *, name: str, vhd, create_option, os_type=None, encryption_settings=None, image=None, caching=None, disk_size_gb: int=None, **kwargs) -> None:
        super(OSDisk, self).__init__(**kwargs)
        self.os_type = os_type
        self.encryption_settings = encryption_settings
        self.name = name
        self.vhd = vhd
        self.image = image
        self.caching = caching
        self.create_option = create_option
        self.disk_size_gb = disk_size_gb
