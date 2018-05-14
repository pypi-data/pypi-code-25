"""
CLI namespace
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright (c) 2015-2018 VMware, Inc.  All rights reserved. '
__license__ = 'SPDX-License-Identifier: MIT'
__docformat__ = 'epytext en'

import logging
from requests.exceptions import SSLError, RequestException

from com.vmware.vapi.std.errors_client import NotFound, OperationNotFound
from vmware.vapi.client.dcli.util import (
    get_console_size,
    get_wrapped_text, print_top_level_help, DCLI_HIDDEN_NAMESPACES)
from vmware.vapi.client.dcli.exceptions import (
    extract_error_msg, handle_ssl_error, handle_connection_error)

logger = logging.getLogger(__name__)


class CliNamespace(object):
    """
    Class to manage operations related to namespace related commands.
    """
    def __init__(self, metadata_manager, path=None, name=None):
        self.metadata_manager = metadata_manager
        self.path = path
        self.name = name

        self.is_namespace = True

        try:
            self.ns_info = self.metadata_manager.get_namespace_info(
                self.path, self.name)
        except NotFound:
            self.is_namespace = False
        except OperationNotFound:
            error_msg = 'Unable to connect to the server.\n'
            error_msg += 'Please make sure CLI service is running.'
            raise Exception(error_msg)
        except SSLError as e:
            handle_ssl_error(e)
        except RequestException as e:
            handle_connection_error(e)
        except Exception as e:
            error_msg = 'Unable to connect to the server.'
            msg = extract_error_msg(e)
            if msg:
                logger.error('Error: %s', msg)
            raise Exception(error_msg)

    def is_a_namespace(self):
        """
        Return if the command is a namespace type

        :rtype:  :class:`bool`
        :return: True if its a namespace else False
        """
        return self.is_namespace

    @staticmethod
    def print_description(name, description, name_max_length, desc_max_length):
        """
        Print the namespace/command description with word-wrapping

        :type  name: :class:`str`
        :param name: Namespace/command name
        :type  description: :class:`str`
        :param description: Namespace/command description
        :type  name_max_length: :class:`int`
        :param name_max_length: Maximum length of a namespace/command
        :type  desc_max_length: :class:`int`
        :param desc_max_length: Maximum length of description per line
        """
        desc_len = len(description)
        if desc_len > desc_max_length:
            desc_list = get_wrapped_text(description, desc_max_length)
            print('{0:{width}}   {1}'.format(name, desc_list[0], width=name_max_length))
            for desc in desc_list[1:]:
                print('{0: >{width}}'.format('', width=name_max_length + 3), end="")
                print(desc)
        else:
            print('{0:{width}}   {1}'.format(name, description, width=name_max_length))

    def print_namespace_help(self, interactive_mode=False):
        """
        Print help of a namespace
        """
        if not self.ns_info.identity.path and not self.ns_info.identity.name:
            print_top_level_help(interactive_mode)
            print()

        _, screen_width = get_console_size()
        desc_list = get_wrapped_text(self.ns_info.description, screen_width)
        for desc in desc_list:
            print(desc)
        print()

        if self.ns_info.children:
            print('Available Namespaces:')
            print()

            ns_data = {}
            ns_max_length = 0

            for child in self.ns_info.children:
                for ns in DCLI_HIDDEN_NAMESPACES:  # if namespace should be hidden don't show it's description
                    if child.path == ns['path'] and child.name == ns['name']:
                        break
                else:
                    try:
                        child_info = self.metadata_manager.get_namespace_info(child.path, child.name)
                    except NotFound:
                        continue

                    if child.name:
                        ns_max_length = len(child.name) if len(child.name) > ns_max_length else ns_max_length
                        ns_data[child.name] = child_info.description

            desc_max_length = screen_width - ns_max_length - 4
            for key in sorted(ns_data.keys()):
                CliNamespace.print_description(key, ns_data[key], ns_max_length, desc_max_length)

        cmd_path = '%s.%s' % (self.ns_info.identity.path,
                              self.ns_info.identity.name)

        try:
            cmd_list = self.metadata_manager.get_commands(cmd_path)
        except NotFound:
            return

        if cmd_list:
            print()
            print('Available Commands:')
            print()

            cmd_data = {}
            cmd_max_length = 0
            for cmd in cmd_list:
                try:
                    cmd_info = self.metadata_manager.get_command_info(cmd.path, cmd.name)
                except NotFound:
                    continue

                cmd_max_length = len(cmd.name) if len(cmd.name) > cmd_max_length else cmd_max_length
                cmd_data[cmd.name] = cmd_info.description

            desc_max_length = screen_width - cmd_max_length - 4
            for key in sorted(cmd_data.keys()):
                CliNamespace.print_description(key, cmd_data[key], cmd_max_length, desc_max_length)
            print()
