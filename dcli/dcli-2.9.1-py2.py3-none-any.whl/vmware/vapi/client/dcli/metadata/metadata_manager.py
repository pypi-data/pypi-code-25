"""
This module provides metadata manager which acts as a wrapper
around metadata provider
"""

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright (c) 2017-2018 VMware, Inc.  All rights reserved. '
__license__ = 'SPDX-License-Identifier: MIT'
__docformat__ = 'epytext en'

from vmware.vapi.client.dcli.metadata.local_metadata_provider import \
    LocalMetadataProvider
from com.vmware.vapi.std.errors_client import NotFound


class MetadataManager(object):
    """
    Wrapper class with additional logic around metadata provider
    """

    def __init__(self, metadata_provider):
        self.metadata_provider = metadata_provider
        self.internal_commands_provider = LocalMetadataProvider(server_type='internal')

    def get_commands(self, namespace_path=None):
        """
        Gets list of commands for the specified namespace_path

        :param namespace_path: namespace path to retrieve commands from
        :type namespace_path: :class:`str`
        :return: list of commands
        :rtype: :class:`list` of
            :class:`vmware.vapi.client.dcli.metadata.metadata_info.
                                                    CommandIdentityMetadataInfo`
        """
        # internal commands should not be overrideable so they should go
        # first in the list
        commands = []
        commands = self.internal_commands_provider.get_commands(namespace_path)
        try:
            commands.extend(self.metadata_provider.get_commands(namespace_path))
        except NotFound:
            pass
        return commands

    def get_command_info(self, namespace_path, command_name):
        """
        Gets command metadata info by specified command name and namespace path

        :param namespace_path: namespace path to the command
        :type namespace_path: :class:`str`
        :param command_name: command name
        :type command_name: :class:`str`
        :return: coomand metdata info object
        :rtype: :class:`vmware.vapi.client.dcli.metadata.metadata_info.
                                                        CommandMetadataInfo`
        """
        try:
            command = self.internal_commands_provider.get_command_info(
                namespace_path, command_name)
        except NotFound:
            command = None

        if command is not None:
            return command

        return self.metadata_provider.get_command_info(namespace_path,
                                                       command_name)

    def get_namespaces(self):
        """
        Gets the list of namespaces

        :return: list of namespace identity objects
        :rtype: :class:`list` of type
            :class:`vmware.vapi.client.dcli.metadata.metadata_info.
                                                NamespaceIdentityMetadataInfo`
        """
        namespaces = self.internal_commands_provider.get_namespaces()
        if namespaces is None:
            namespaces = []
        namespaces.extend(self.metadata_provider.get_namespaces())

        return namespaces

    def get_namespace_info(self, namespace_path, namespace_name):
        """
        Gets namesapce metadata info for specified namespace path and name

        :param namespace_path: namespace path
        :type namespace_path: :class:`str`
        :param namespace_name: namespace name
        :type namespace_name: :class:`str`
        :return: Namespace info object found by given path and name
        :rtype: :class:`vmware.vapi.client.dcli.metadata.metadata_info.
                                                        NamespaceMetadataInfo`
        """
        namespace = None
        if namespace_path != '' and namespace_name != '':
            try:
                namespace = self.internal_commands_provider.get_namespace_info(
                    namespace_path, namespace_name)
            except NotFound:
                namespace = None

        if namespace is not None:
            return namespace

        return self.metadata_provider.get_namespace_info(namespace_path, namespace_name)

    def get_command_input_definition(self, service_path, operation_name):
        """
        Gets vapi input definition for a command specified by path and name

        :param service_path: service path where the operation resides
        :type service_path: :class:`str`
        :param operation_name: operation name
        :type operation_name: :class:`str`
        :return: Input definition object for an operation specified by
        service path and operation name
        :rtype: :class:`vmware.vapi.data.definition.StructDefinition`
        """
        return self.metadata_provider.get_command_input_definition(
            service_path, operation_name)

    def get_structure_info(self, structure_path):
        """
        Gets metadata for structure specified by structure path

        :param structure_path: structure path
        :type structure_path: :class:`str`
        :return: Strucutre info object found by specified structure path
        :rtype: :class:`vmware.vapi.client.dcli.metadata.metadata_info.
                                                                StructureInfo
        """
        return self.metadata_provider.get_structure_info(structure_path)

    def get_enumeration_info(self, enumeration_path):
        """
        Gets metadata for enumeration specified by enumeration path

        :param enumeration_path: enumeration path
        :type enumeration_path: :class:`str`
        :return: Enumeration info object specified by enumeration path
        :rtype: :class:`vmware.vapi.client.dcli.metadata.metadata_info.
                                                                EnumerationInfo
        """
        return self.metadata_provider.get_enumeration_info(enumeration_path)

    def get_operation_info(self, operation_path, operation_name):
        """
        Gets metadata for operation specified by operation path and operation
        name

        :param operation_path: operation path
        :type operation_path: :class:`str`
        :param operation_name: operation name
        :type operation_name: :class:`str`
        :return: operation info object specified by operation path and
        operation name
        :rtype: :class:`vmware.vapi.client.dcli.metadata.metadata_info.
                                                                OperationInfo
        """
        return self.metadata_provider.get_operation_info(operation_path,
                                                         operation_name)

    def get_authentication_schemes(self, operation_path, operation_name):
        """
        Gets authentication schema for an operation specified by operation
        path and operation name

        :param operation_path: operation path
        operation resides
        :type operation_path: :class:`str`
        :param operation_name: operation name
        :type operation_name: :class:`str`
        :return: authentication schema for a specified operation
        :rtype: :class:`dict` of :class:`str` and :class:`list` of :class:`str`
        """
        if operation_path.startswith('dcli_internal_command'):
            return None

        return self.metadata_provider.get_authentication_schemes(
            operation_path, operation_name)
