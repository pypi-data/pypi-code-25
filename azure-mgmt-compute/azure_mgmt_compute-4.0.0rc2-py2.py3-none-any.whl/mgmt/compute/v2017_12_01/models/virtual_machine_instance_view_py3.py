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


class VirtualMachineInstanceView(Model):
    """The instance view of a virtual machine.

    :param platform_update_domain: Specifies the update domain of the virtual
     machine.
    :type platform_update_domain: int
    :param platform_fault_domain: Specifies the fault domain of the virtual
     machine.
    :type platform_fault_domain: int
    :param computer_name: The computer name assigned to the virtual machine.
    :type computer_name: str
    :param os_name: The Operating System running on the virtual machine.
    :type os_name: str
    :param os_version: The version of Operating System running on the virtual
     machine.
    :type os_version: str
    :param rdp_thumb_print: The Remote desktop certificate thumbprint.
    :type rdp_thumb_print: str
    :param vm_agent: The VM Agent running on the virtual machine.
    :type vm_agent:
     ~azure.mgmt.compute.v2017_12_01.models.VirtualMachineAgentInstanceView
    :param maintenance_redeploy_status: The Maintenance Operation status on
     the virtual machine.
    :type maintenance_redeploy_status:
     ~azure.mgmt.compute.v2017_12_01.models.MaintenanceRedeployStatus
    :param disks: The virtual machine disk information.
    :type disks: list[~azure.mgmt.compute.v2017_12_01.models.DiskInstanceView]
    :param extensions: The extensions information.
    :type extensions:
     list[~azure.mgmt.compute.v2017_12_01.models.VirtualMachineExtensionInstanceView]
    :param boot_diagnostics: Boot Diagnostics is a debugging feature which
     allows you to view Console Output and Screenshot to diagnose VM status.
     <br><br> For Linux Virtual Machines, you can easily view the output of
     your console log. <br><br> For both Windows and Linux virtual machines,
     Azure also enables you to see a screenshot of the VM from the hypervisor.
    :type boot_diagnostics:
     ~azure.mgmt.compute.v2017_12_01.models.BootDiagnosticsInstanceView
    :param statuses: The resource status information.
    :type statuses:
     list[~azure.mgmt.compute.v2017_12_01.models.InstanceViewStatus]
    """

    _attribute_map = {
        'platform_update_domain': {'key': 'platformUpdateDomain', 'type': 'int'},
        'platform_fault_domain': {'key': 'platformFaultDomain', 'type': 'int'},
        'computer_name': {'key': 'computerName', 'type': 'str'},
        'os_name': {'key': 'osName', 'type': 'str'},
        'os_version': {'key': 'osVersion', 'type': 'str'},
        'rdp_thumb_print': {'key': 'rdpThumbPrint', 'type': 'str'},
        'vm_agent': {'key': 'vmAgent', 'type': 'VirtualMachineAgentInstanceView'},
        'maintenance_redeploy_status': {'key': 'maintenanceRedeployStatus', 'type': 'MaintenanceRedeployStatus'},
        'disks': {'key': 'disks', 'type': '[DiskInstanceView]'},
        'extensions': {'key': 'extensions', 'type': '[VirtualMachineExtensionInstanceView]'},
        'boot_diagnostics': {'key': 'bootDiagnostics', 'type': 'BootDiagnosticsInstanceView'},
        'statuses': {'key': 'statuses', 'type': '[InstanceViewStatus]'},
    }

    def __init__(self, *, platform_update_domain: int=None, platform_fault_domain: int=None, computer_name: str=None, os_name: str=None, os_version: str=None, rdp_thumb_print: str=None, vm_agent=None, maintenance_redeploy_status=None, disks=None, extensions=None, boot_diagnostics=None, statuses=None, **kwargs) -> None:
        super(VirtualMachineInstanceView, self).__init__(**kwargs)
        self.platform_update_domain = platform_update_domain
        self.platform_fault_domain = platform_fault_domain
        self.computer_name = computer_name
        self.os_name = os_name
        self.os_version = os_version
        self.rdp_thumb_print = rdp_thumb_print
        self.vm_agent = vm_agent
        self.maintenance_redeploy_status = maintenance_redeploy_status
        self.disks = disks
        self.extensions = extensions
        self.boot_diagnostics = boot_diagnostics
        self.statuses = statuses
