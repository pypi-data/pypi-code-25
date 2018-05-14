#!/usr/bin/env python
"""
CLI command
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright (c) 2015-2018 VMware, Inc.  All rights reserved. '
__license__ = 'SPDX-License-Identifier: MIT'
__docformat__ = 'epytext en'

import sys
import logging
import importlib
import json
import six

from com.vmware.vapi.std.errors_client import NotFound, OperationNotFound
from vmware.vapi.client.dcli.util import (
    ArgumentInfo, CliHelper, CliArgParser, CliHelpFormatter, StatusCode,
    BoolAction, BoolAppendAction,
    is_field_union_tag, is_field_union_case, get_metadata_field_info,
    union_case_matches_union_tag_value, CliGenericTypes,
    TypeInfoGenericTypes, ServerTypes)
from vmware.vapi.client.dcli.exceptions import handle_error, handle_server_error
from vmware.vapi.data.definition import (
    DynamicStructDefinition, StructDefinition, StringDefinition,
    IntegerDefinition, DoubleDefinition, BooleanDefinition,
    ListDefinition, OptionalDefinition)
from vmware.vapi.bindings.struct import VapiStruct
from vmware.vapi.data.type import Type
from vmware.vapi.data.value import (
    StructValue, StringValue, IntegerValue, DoubleValue, SecretValue,
    BooleanValue, BlobValue, OptionalValue, ListValue)
from vmware.vapi.lib.constants import MAP_ENTRY
from vmware.vapi.lib.rest import OperationRestMetadata
from vmware.vapi.core import MethodResult
from vmware.vapi.data.serializers.cleanjson import DataValueConverter
from vmware.vapi.provider.filter import ApiProviderFilter

try:
    import argparse
except ImportError as e:
    print('Error: No argparse module present quitting.', file=sys.stderr)
    sys.exit(StatusCode.INVALID_ENV)


data_type_dict = {
    int: 'int',
    str: 'string',
    bool: 'bool',
    float: 'double'
}

logger = logging.getLogger(__name__)


class CliCommand(object):
    """
    Class to manage operations related to actual commands.
    """
    def __init__(self, server_type, connector, metadata_manager,
                 default_options,
                 path=None, name=None):
        self.server_type = server_type
        self.connector = connector
        self.api_provider = connector.get_api_provider()
        self.metadata_manager = metadata_manager
        self.path = path
        self.name = name
        self.input_def = None
        self.secret_map = None
        self.cmd_info = None
        self.current_structure_union_tags = None
        self.default_options = default_options

        if isinstance(self.api_provider, ApiProviderFilter):
            # Get the API Provider (last provider in the chain)
            self.last_api_provider = self.api_provider.get_api_provider()
        else:
            self.last_api_provider = self.api_provider
        if self.server_type in (ServerTypes.NSX, ServerTypes.VMC):
            # Set to use REST Native format instead of vAPI REST
            self.last_api_provider.set_rest_format(False)

        self.is_cmd = True

        try:
            self.cmd_info = self.metadata_manager.get_command_info(path, name)
        except NotFound:
            self.is_cmd = False

    def prompt_for_secret_fields(self, args):
        """
        Method to prompt for secret fields

        :type  args: :class:`argparse.Namespace`
        :param args: Parsed input command arguments object
        """
        for key, prompt in six.iteritems(self.secret_map):
            option_val = getattr(args, key)

            # Only prompt for secret options if they are passed on command line
            # without value. If secret option is not passed on command line
            # option_val will be None. If secret option is passed but no value
            # given option_val will be False. If option is passed along with
            # value then option_val will contain the value.
            # We only need to prompt for cases where option_val is False.
            # For list of secrets any of the input option values can be False
            # for which we need to prompt the user.
            if option_val is False:
                secret_val = CliHelper.prompt_for_secret(prompt)
                setattr(args, key, secret_val)
            elif isinstance(option_val, list) and False in option_val:
                secret_val = []
                for val in option_val:
                    if val is False:
                        tmp_val = CliHelper.prompt_for_secret(prompt)
                        secret_val.append(tmp_val)
                    else:
                        secret_val.append(val)
                setattr(args, key, secret_val)

    def is_a_command(self):
        """
        Return if the command is of command type

        :rtype:  :class:`bool`
        :return: True if its a command else False
        """
        return self.is_cmd

    def get_input_arg_info(self, arg, add_dynamic_struct_option=False):
        """
        Get the list ArgumentInfo objects for all command input options

        :type  arg: :class:`vmware.vapi.metadata.cli.command.OptionInfo`
        :param arg: CLI command option info structure
        :type  add_dynamic_struct_option: :bool:
        :param add_dynamic_struct_option: Flag to add dynamic struct option

        :rtype:  :class:`list` of :class:`ArgumentInfo`
        :return: List of ArgumentInfo object containing struct field details
        """
        if add_dynamic_struct_option:
            # For older metadata versions with dynamicstruct input
            display_name = '--%s' % (arg.field_name.split('.')[0])
            generic_type = 'optional'
        else:
            display_name = '--%s' % (arg.long_option)
            generic_type = arg.generic

        short_name = '-%s' % (arg.short_option) if arg.short_option else None
        description = arg.description
        arg_type = arg.type

        arg_action = 'append' if self.is_generic_list(generic_type) else 'store'

        type_ = CliHelper.convert_vapi_to_python_type(arg_type)

        if type_ == bool:
            type_ = str
            arg_action = BoolAppendAction if self.is_generic_list(generic_type) else BoolAction

        arg_desc = ''

        if generic_type == 'list':
            data_type_str = 'list of '
        elif generic_type == 'list_optional':
            data_type_str = 'list of optional '
        elif generic_type == 'optional_list':
            data_type_str = 'optional list of '
        elif generic_type == 'optional':
            data_type_str = ''
        else:
            arg_desc = 'required:'
            data_type_str = ''

        arg_nargs = None

        if arg_type == 'secret':
            arg_nargs = '?'
            data_type_str = '%ssecret ' % data_type_str

        if arg_type in ['complex', 'complex-hasfieldsof']:
            data_type_str = '(%sjson input)' % (data_type_str)
            tmp_desc = '%s %s' % (description, data_type_str)
            type_ = str
        elif arg_type == 'dynamicstructure' or add_dynamic_struct_option:
            data_type_str = '(%sjson input)' % (data_type_str)
            tmp_desc = '%s struct %s' % (display_name.lstrip('--'), data_type_str)
            type_ = str
        elif arg_type == 'binary':
            type_ = argparse.FileType('rb')
            data_type_str = '(%s file input)' % (data_type_str)
            tmp_desc = '%s %s' % (description, data_type_str)
        else:
            data_type_str = '(%s%s)' % (data_type_str,
                                        data_type_dict.get(CliHelper.convert_vapi_to_python_type(arg_type), 'string'))
            tmp_desc = '%s %s' % (description, data_type_str)
        option_default_value = self.get_input_arg_default_value(arg)

        if arg_desc and option_default_value is None:
            arg_desc = '%s %s' % (arg_desc, tmp_desc)
        else:
            arg_desc = tmp_desc

        arg_info = ArgumentInfo()
        arg_info.short_name = short_name
        arg_info.name = display_name
        arg_info.arg_action = arg_action
        arg_info.description = arg_desc
        arg_info.required = (generic_type != 'optional' and
                             generic_type != 'optional_list' and
                             generic_type != 'list_optional')
        arg_info.nargs = arg_nargs

        if option_default_value is not None:
            arg_info.default = option_default_value
            arg_info.required = False

        # Handle enumeration case. Only in case of enum types
        # we store fully qualified names, for all others its type name
        if arg_type.find('.') != -1:
            try:
                enum_info = self.metadata_manager.get_enumeration_info(
                    arg_type)
                arg_info.choices = enum_info.values if enum_info else []
            except OperationNotFound:
                pass
            except NotFound:
                pass

        if arg_type == 'secret':
            tmp_name = display_name.lstrip('--')
            self.secret_map[tmp_name.replace('-', '_')] = '%s: ' % tmp_name
            arg_info.const = False
        else:
            # XXX need to handle blob and opaque
            arg_info.type_ = type_

        return [arg_info]

    def get_input_arg_default_value(self, arg):
        """
        Gets default value for given argument from env profiles options

        :type  arg: :class:`vmware.vapi.metadata.cli.command.OptionInfo`
        :param arg: CLI command option info structure

        :rtype:  :class:`str`
        :return: default value for argument
        """
        # set default value from default options in configuration if present
        module = CliHelper.get_module_name(self.server_type)
        if not self.default_options:
            return None
        return self.default_options.try_get(arg.long_option, module=module)

    @classmethod
    def is_generic_list(cls, generic_type):
        """
        Checks whether given generic_type is represention of list or optional list or list of optionals

        :type  arg: :class:`str`
        :param generic_type: generict type to be checked

        :rtype:  :class:`boolean`
        :return: boolean indicating whether generic_type is represention of list or optional list
        """
        return generic_type == 'list' or \
            generic_type == 'optional_list' or \
            generic_type == 'list_optional'

    def get_parser_arguments(self):
        """
        Method to get vAPI command argument details struct list for a specific command

        :rtype:  :class:`StatusCode`
        :return: Status code
        :rtype:  :class:`list` of :class:`ArgumentInfo`
        :return: List of ArgumentInfo object containing struct field details
        """
        input_arg_details = []
        retval = StatusCode.SUCCESS
        self.secret_map = {}

        self.input_def = self.cmd_info.input_definition
        for arg in self.cmd_info.options:  # pylint: disable=too-many-nested-blocks
            if arg.type in ['map', 'opaque', 'void']:
                error_msg = '%s input type not supported' % arg.type.title()
                handle_error(error_msg)
                retval = StatusCode.INVALID_COMMAND
                break

            # Needed for compatibility with older version of CLI metadata
            # for dynamic struct inputs
            # For struct and dynamic struct inputs
            if arg.field_name.find('.') != -1 or arg.type == 'dynamicstructure':
                if self.input_def:
                    if self.input_def.get_field(arg.field_name.split('.')[0]).type == Type.LIST:
                        handle_error('List of structure type not supported')
                        retval = StatusCode.INVALID_COMMAND
                        break
                    elif arg.field_name.find('.') != -1:
                        field_name = arg.field_name.split('.')[0]
                        field_input_def = self.input_def.get_field(field_name)
                        if isinstance(field_input_def, DynamicStructDefinition):
                            # For HasFieldsOf case add extra argument for purely
                            # dynamic structure json input
                            arg_info = self.get_input_arg_info(arg, True)

                            # Check if argument is already in the list
                            has_arg = [arg_detail for arg_detail in input_arg_details
                                       if input_arg_details and arg_detail.name == arg_info[0].name]

                            # If the argument doesn't exist add it to list
                            if not has_arg:
                                input_arg_details += arg_info

            arg_info = self.get_input_arg_info(arg)
            input_arg_details += arg_info

        return retval, input_arg_details

    def add_parser_argument(self, parser):
        """
        Method to add vAPI command arguments to the CliArgParser object

        :type  parser: :class:`CliArgParser`
        :param parser: CliArgParser object

        :rtype:  :class:`StatusCode`
        :return: Status code
        """
        group = parser.add_argument_group('Input Arguments')
        retval, input_args = self.get_parser_arguments()
        if retval == StatusCode.SUCCESS:
            group.add_argument('-h', '--help', action='help', help='show this help message and exit')
            for arg in input_args:
                kwargs = {
                    'action': arg.arg_action,
                    'const': arg.const,
                    'nargs': arg.nargs,
                    'required': arg.required,
                    'help': arg.description,
                }

                if arg.default is not None:
                    kwargs['default'] = arg.default

                if arg.const is not False:
                    kwargs['type'] = arg.type_
                    kwargs['choices'] = arg.choices

                # Make all list inputs optional as VMODL2 required lists can be empty
                if arg.arg_action == 'append':
                    kwargs['required'] = False
                    # If its a required list input set a default value as empty list
                    if arg.required:
                        kwargs['default'] = []

                if arg.short_name:
                    group.add_argument(arg.short_name, arg.name, **kwargs)
                else:
                    group.add_argument(arg.name, **kwargs)

        return retval

    def build_has_fields_of_value(self, input_dict, input_tuple, struct_name,
                                  field_split, field_input_value, index):
        """
        Method to create struct value for @HasFieldsOf input fields

        :type  input_dict: :class:`dict`
        :param input_dict: Dictionary of input values
        :type  field_split: :class:`list` of :class:`str`
        :param field_split: Split of input field name
        :type  field_input_value: :class:`vmware.vapi.data.value.StructValue`
        :param field_input_value: Empty StructValue to be set
        :type  index: :class:`int`
        :param index: Index of nested struct
        """
        field_name = field_split[index]
        field_val = input_dict[field_name]
        struct_id = None
        generic_type = None

        for key, value in six.iteritems(field_val):  # pylint: disable=too-many-nested-blocks
            if isinstance(value, dict):
                try:
                    # Find the full struct id from struct name by using
                    # metamodel structure interface
                    struct_info = self.metadata_manager.get_structure_info(
                        struct_name)
                    for field in struct_info.fields:
                        if field.name == key:
                            try:
                                struct_id = field.type.user_defined_type.resource_id
                            except AttributeError:
                                generic_type = field.type.generic_instantiation.generic_type
                                struct_id = field.type.generic_instantiation.element_type.user_defined_type.resource_id
                except Exception:
                    logger.info('Unable to get struct info for struct %s from metamodel service', struct_name)

                if struct_id:
                    struct_val = StructValue(struct_id)
                else:
                    struct_val = StructValue(key)

                # Recursively call the function for nested dynamic struct case
                # We are calling this function once for a dynamic struct, but we
                # will receive only one of the struct fields in the argument
                # name we receive in field split
                if field_split[index + 1] == key:
                    # If the struct field name (key) we are traversing is same as the struct field name we have
                    # in the field split then do recursive call by just incrementing split index
                    self.build_has_fields_of_value(field_val, input_tuple,
                                                   struct_name, field_split,
                                                   struct_val, index + 1)
                else:
                    # If the struct field name (key) we are traversing is different from the struct field name we have
                    # in the field split then find the correct field split by traversing over input tuple
                    input_field_name = [input_val for input_val in input_tuple if input_val[0].split('.')[index + 1] == key][0][0]
                    tmp_field_split = input_field_name.split('.')
                    self.build_has_fields_of_value(field_val, input_tuple,
                                                   struct_name,
                                                   tmp_field_split,
                                                   struct_val, index + 1)
                if generic_type == TypeInfoGenericTypes.optional_type:
                    field_input_value.set_field(key, OptionalValue(struct_val))
                else:
                    field_input_value.set_field(key, struct_val)
            else:
                full_name = '%s.%s' % ('.'.join(field_split[0:index + 1]), key)
                # Get generic and type from CLI metadata and create corresponding data value
                arg = None
                for arg in self.cmd_info.options:
                    if arg.field_name == full_name:
                        break
                field_is_generic = False
                if arg.generic:
                    # if arg is in a structure it is not clear whether the
                    # structure should be of generic type or the field itself.
                    # Need to deduce this from metamodel.
                    if len(full_name.split('.')) > 1:
                        struct_info = self.metadata_manager.get_structure_info(
                            field_input_value.name)
                        field = None
                        for s_field in struct_info.fields:
                            if s_field.name == key:
                                field = s_field
                                break
                        if field is not None and \
                                field.type.category == 'GENERIC':
                            field_is_generic = True
                if arg.generic == CliGenericTypes.list_type:
                    if field_is_generic:
                        data_value = ListValue()
                        for val in value:
                            tmp_value = CliCommand.get_data_value(arg.type, val)
                            data_value.add(tmp_value)
                    else:
                        data_value = value
                elif arg.generic == CliGenericTypes.optional_type:
                    data_value = CliCommand.get_data_value(arg.type, value)
                    if field_is_generic:
                        data_value = OptionalValue(data_value)
                else:
                    data_value = CliCommand.get_data_value(arg.type, value)
                field_input_value.set_field(key, data_value)

    def build_data_value(self, py_value, data_def, struct_name=None):
        """
        Converts a native python value to data value
        using the provided data definition

        :type  py_value: :class:`object`
        :param py_value: Python native value
        :type  data_def: :class:`vmware.vapi.data.definition.DataDefinition`
        :param data_def: Data definition
        :rtype: :class:`vmware.vapi.data.value.DataValue`
        :return: Data value
        """
        output_val = None
        if data_def.type == Type.OPTIONAL:
            output_val = data_def.new_value()
            if py_value is not None:
                output_val.value = self.build_data_value(py_value,
                                                         data_def.element_type)
        elif data_def.type == Type.LIST:
            output_val = data_def.new_value()
            if py_value:
                for element in py_value:
                    output_val.add(self.build_data_value(element, data_def.element_type))
        elif data_def.type in (Type.STRUCTURE, Type.ERROR):
            output_val = data_def.new_value()
            for field in data_def.get_field_names():
                field_def = data_def.get_field(field)

                if py_value is None:
                    if field_def.type == Type.OPTIONAL:
                        output_val.set_field(field,
                                             OptionalValue())
                    else:
                        raise Exception('Invalid input type')
                else:
                    if isinstance(py_value, dict):
                        value = py_value.get(field)
                    # If Class used in python bindings is the struct
                    elif isinstance(py_value, VapiStruct):
                        value = py_value.get_field(field)
                    else:
                        raise Exception('Invalid input type')
                    output_val.set_field(field,
                                         self.build_data_value(value,
                                                               data_def.get_field(field),
                                                               struct_name))
        elif data_def.type == Type.DYNAMIC_STRUCTURE:
            output_val = StructValue(struct_name)
            py_type_map = {
                str: StringDefinition,
                int: IntegerDefinition,
                float: DoubleDefinition,
                bool: BooleanDefinition,
                dict: DynamicStructDefinition,
                list: ListDefinition,
                None: OptionalDefinition
            }
            if six.PY2:
                py_type_map[unicode] = StringDefinition  # pylint: disable=E0602
                py_type_map[long] = IntegerDefinition  # pylint: disable=E0602

            for k, v in six.iteritems(py_value):
                field_data_def_type = py_type_map.get(type(v))
                if v is None:
                    field_data_def = OptionalDefinition(StringDefinition())
                elif isinstance(v, list):
                    if v:
                        field_data_def = field_data_def_type(py_type_map.get(type(v[0]))())
                    else:
                        field_data_def = ListDefinition(StringDefinition())
                else:
                    try:
                        field_data_def = field_data_def_type()
                        struct_name = k
                    except TypeError:
                        field_data_def = StringDefinition()
                output_val.set_field(k, self.build_data_value(v, field_data_def, struct_name))
        elif data_def.type == Type.VOID:
            output_val = data_def.new_value()
        elif data_def.type == Type.BLOB:
            # For Binary input user passes a file with binary data
            # on command line. And argparse gives us a file object
            py_value.seek(0)
            blob_value = py_value.read()
            output_val = data_def.new_value(blob_value)
        elif data_def.type == Type.OPAQUE:
            raise Exception('Unsupported input type OPAQUE')
        # Primitive type Integer/Double/String/Boolean/Secret
        else:
            output_val = data_def.new_value(py_value)
        return output_val

    @staticmethod
    def get_data_value(data_type, value):
        """
        Method to convert data type and value to DataValue object

        :type  data_type: :class:`str`
        :param data_type: Data type of the parameter
        :type  value: :class:`type`
        :param value: Value of the parameter

        :rtype:  :class:`vmware.vapi.data.value.DataValue`
        :return: DataValue corresponding to the input type
        """
        if data_type == 'boolean':
            return BooleanValue(value)
        elif data_type == 'double':
            return DoubleValue(value)
        elif data_type == 'long':
            return IntegerValue(value)
        elif data_type == 'secret':
            return SecretValue(value)
        elif data_type == 'binary':
            return BlobValue(value)
        return StringValue(value)

    def get_command_parser(self):
        """
        Get the command parser for vAPI command

        :rtype:  :class:`StatusCode`
        :return: Status code
        :rtype:  :class:`CliArgParser`
        :return: CLI argument parser
        """
        cmd_name = '%s %s' % (' '.join(self.cmd_info.identity.path.split('.')),
                              self.cmd_info.identity.name)
        parser = CliArgParser(prog=cmd_name,
                              description=self.cmd_info.description,
                              formatter_class=CliHelpFormatter,
                              add_help=False)

        retval = self.add_parser_argument(parser)
        return retval, parser

    def dictize_command_input(self, input_tuple, input_dict):
        """
        Method to convert a command input tuple into nested input dictionary

        :type   input_tuple: :class:`tuple`
        :param  input_tuple: Input command options tuple
        :type   input_dict: :class:`dict`
        :param  input_dict: Nested input dictionary
        """
        for key, val in input_tuple:
            parts = key.split('.', 1)
            if len(parts) > 1:
                branch = input_dict.setdefault(parts[0], {})
                self.dictize_command_input([(parts[1], val)], branch)
            else:
                input_dict[parts[0]] = val

    @staticmethod
    def get_json_input(json_value):
        """
        Method to get JSON input from command line

        :type   json_value: :class:`str`
        :param  json_value: JSON input value or file name

        :rtype:  :class:`str`
        :return: Parsed JSON value as string
        """
        value = ''
        if json_value.lstrip()[0] in ['{', '[']:
            try:
                value = json.loads(json_value)
            except ValueError as e:
                raise Exception('Invalid json value provided. %s' % str(e))
        else:  # Else expect a json input file
            with open(json_value, 'r') as fp:
                value = json.load(fp)
        return value

    def set_command_args(self, cmd_input, input_value):
        """
        Method to set input values from command input

        :type  cmd_input: :class:`dict`
        :param cmd_input: Command input dict
        :type  input_value: :class:`vmware.vapi.data.value.StructValue`
        :param input_value: Input StructValue
        """
        # create a map of option name to option info
        option_map = {}
        for option in self.cmd_info.options:
            # have to replace '-' with '_' because argparse
            # stores the variable name with '_'
            if option.type != 'complex-hasfieldsof':
                option_map[option.long_option.replace('-', '_')] = option

        # convert the option name to the vAPI field name in the cmd_field_input
        cmd_field_input = {}
        dynamic_struct_val = {}
        for k, v in six.iteritems(cmd_input.__dict__):
            try:
                cmd_field_input[option_map[k].field_name] = v
            except KeyError:
                # Handle case for extra json input parameter added
                dynamic_struct_val[k] = v

        input_dict = {}
        input_tuple = [(key, val) for key, val in six.iteritems(cmd_field_input) if val is not None and not (isinstance(val, list) and len(val) == 0)]
        self.dictize_command_input(input_tuple, input_dict)

        filtered_args = []
        dynamic_struct_args = {}
        # iterate only over arguments provided on commandline.
        for arg in filter(lambda x: x.field_name in dict(input_tuple), self.cmd_info.options):  # pylint: disable=W0110
            field_split = arg.field_name.split('.')
            if len(field_split) == 1:
                filtered_args.append(arg)
            else:
                field_input_def = self.input_def.get_field(field_split[0])
                if isinstance(field_input_def, DynamicStructDefinition):
                    # Add only one entry per dynamic struct option
                    dynamic_struct_args[field_split[0]] = arg
                else:
                    filtered_args.append(arg)

        if dynamic_struct_args:
            filtered_args += list(dynamic_struct_args.values())

        # go through filtered_args additionally and beforehand to resolve any
        # json input
        for arg in filtered_args:
            if arg.type in ['complex', 'complex-hasfieldsof']:
                # each leaf of inpput_dict which is complex should
                # expand it's json value to dictionary
                tmp_val = input_dict
                field_names = arg.field_name.split('.')
                next_field_index = 0
                while isinstance(tmp_val, dict):
                    if not isinstance(tmp_val[field_names[next_field_index]],
                                      dict):
                        break
                    tmp_val = tmp_val[field_names[next_field_index]]
                    next_field_index += 1
                tmp_val[field_names[next_field_index]] = \
                    CliCommand.get_json_input(tmp_val[field_names[next_field_index]])

        # Loop over all the input args once
        for arg in filtered_args:
            data_value = None
            field_name = arg.field_name.split('.')[0]
            field_input_def = self.input_def.get_field(field_name)
            if isinstance(field_input_def, DynamicStructDefinition):
                # Get the full struct name from metamodel operation interface
                try:
                    operation_info = \
                        self.metadata_manager.get_operation_info(
                            self.cmd_info.service_id,
                            self.cmd_info.operation_id)
                    operation_param = [param for param in operation_info.params
                                       if param.name == field_name][0]
                    struct_name = operation_param.has_fields_of_struct_name \
                        if operation_param.has_fields_of_struct_name else field_name
                except Exception:
                    struct_name = field_name

                field_split = arg.field_name.split('.')
                # Create an empty struct value and add all the fields
                # In case the field is a struct add all the fields in it recursively
                data_value = StructValue(struct_name)

                if len(field_split) > 1:
                    # @HasFieldsOf case with extra json input param
                    json_value = dynamic_struct_val[field_split[0]]
                else:
                    json_value = input_dict[struct_name]

                if json_value:
                    if not isinstance(json_value, dict):
                        value = CliCommand.get_json_input(json_value)
                    else:
                        value = json_value
                    data_value = self.build_data_value(value, field_input_def, struct_name)

                # For @HasFieldsOf input
                if len(field_split) > 1:
                    self.build_has_fields_of_value(input_dict, input_tuple, struct_name, field_split, data_value, 0)
            else:
                value = input_dict[field_name]
                data_value = self.build_data_value(value, field_input_def)

            if data_value:
                input_value.set_field(field_name, data_value)

        # iterate over arguments not passed on the command line
        # special case needed to handle required empty struct
        for arg in filter(lambda x: x.field_name.split('.')[0] not in list(input_dict.keys()), self.cmd_info.options):  # pylint: disable=W0110
            data_value = None
            field_name = arg.field_name.split('.')[0]
            field_input_def = self.input_def.get_field(field_name)
            if isinstance(field_input_def, StructDefinition):
                data_value = self.build_data_value({}, field_input_def)
                input_value.set_field(field_name, data_value)

    def execute_command(self, ctx, dcli_ctx, cmd_input, service_id,
                        operation_id):
        """
        Method to execute vAPI operations

        :type  ctx: :class:`vmware.vapi.core.ExecutionContext`
        :param ctx: Execution context for this method
        :type  cmd_input: :class:`dict`
        :param cmd_input: Command input dict

        :rtype:  :class:`vmware.vapi.core.MethodResult`
        :return: MethodResult for the vAPI operation
        """
        # If we can't get input definition raise error
        if service_id.startswith('env.'):
            return self.execute_internal_command(service_id,
                                                 operation_id,
                                                 cmd_input,
                                                 dcli_ctx)

        if self.input_def is None:
            error_msg = 'Unable to find operation %s' % (
                self.cmd_info.identity.name)
            error_msg += ' in service %s' % (self.cmd_info.identity.path)
            logger.error(error_msg)
            raise Exception(error_msg)
        else:
            input_value = self.input_def.new_value()
            self.set_command_args(cmd_input, input_value)
        logger.info('Invoking vAPI operation %s for service %s',
                    self.cmd_info.operation_id, self.cmd_info.service_id)

        if self.server_type in (ServerTypes.NSX, ServerTypes.VMC):
            rest_metadata = self.get_rest_metadata()
            self.last_api_provider.add_rest_metadata(self.cmd_info.service_id,
                                                     self.cmd_info.operation_id,
                                                     rest_metadata)

        return self.api_provider.invoke(self.cmd_info.service_id,
                                        self.cmd_info.operation_id,
                                        input_value,
                                        ctx)

    def execute_internal_command(self, service_id, operation_id, cmd_input,
                                 dcli_ctx):
        """
        Method to execute internal dcli operation

        :type  service_id: :class:`str`
        :param service_id: service id of the operation
        :type  operation_id: :class:`str`
        :param operation_id: operation id
        :type  cmd_input: :class:`argparse.Namespace
        :param cmd_input: Command input dict

        :rtype:  :class:`vmware.vapi.core.MethodResult`
        :return: MethodResult for the internal operation
        """
        class_name = service_id.split('.')[-1].capitalize()
        module_name = 'vmware.vapi.client.dcli.internal_commands.%s' % \
                      service_id[(service_id.index('.') + 1):]
        module = importlib.import_module(module_name)
        class_instance = getattr(module, class_name)(dcli_ctx)

        # replace long_option param name with field_name
        for option in self.cmd_info.options:
            long_option_name = option.long_option.replace('-', '_')
            if long_option_name in cmd_input and \
                    option.field_name != long_option_name:
                cmd_input[option.field_name] = \
                    cmd_input[long_option_name]
                del cmd_input[long_option_name]

        result = getattr(class_instance, operation_id)(**vars(cmd_input))

        self.update_default_options(service_id, operation_id)

        data_value_result = DataValueConverter.convert_to_data_value(
            json.dumps(result))
        return MethodResult(output=data_value_result)

    def update_default_options(self, service_id, operation_id):
        """
        Method reload default options from configuration file
        if needed

        :type  service_id: :class:`str`
        :param service_id: service id of the operation
        :type  operation_id: :class:`str`
        :param operation_id: operation id
        """
        if self.default_options and \
                CliCommand.internal_command_needs_update(service_id, operation_id):
            self.default_options.load_configuration_file()

    @staticmethod
    def internal_command_needs_update(service_id, operation_id):
        """
        Returns True if operation needs update after execution of
        another internal command

        :type  service_id: :class:`str`
        :param service_id: service id of the operation
        :type  operation_id: :class:`str`
        :param operation_id: operation id
        """
        return \
            (service_id == 'env.options' and operation_id in ('set', 'delete')) or \
            (service_id == 'env.profiles' and operation_id == 'delete') or \
            (service_id == 'env.profiles.default' and operation_id == 'set')

    def get_rest_metadata(self):
        """
        Collects operation specific rest metadata, if any, for execution of
        dcli command

        :rtype :class:`vmware.vapi.lib.rest.OperationRestMetadata`
        :return: OperationRestMetadata object with needed rest metadata for
            executing command
        """
        return OperationRestMetadata(
            http_method=self.cmd_info.rest_info.http_method,
            url_template=self.cmd_info.rest_info.url_template,
            request_body_parameter=self.cmd_info.rest_info.request_body_field,
            path_variables=self.cmd_info.rest_info.path_variable_map,
            query_parameters=self.cmd_info.rest_info.request_param_map
        )

    def display_result(self, output, out_formatter, more):
        """
        Print the vAPI operation result

        :type  output: :class:`vmware.vapi.core.MethodResult`
        :param output: MethodResult for vAPI operation
        :type  out_formatter: :class:`vmware.vapi.client.lib.Formatter`
        :param out_formatter: Output formatter

        :rtype:  :class:`StatusCode`
        :return: Method status
        """
        output_structures_metadata = self.collect_output_structures_metadata()

        if output.success():
            out_formatter.apply_structure_filter_visitor(
                self.formatter_apply_structure_filter_visitor)
            out_formatter.structure_element_visit(
                self.formatter_structure_element_visit)
            out_formatter.format_output(
                output.output,
                more,
                self.cmd_info.output_field_list,
                output_structures_metadata)

        if output.error is not None:
            handle_server_error(output.error)
            if self.server_type in (ServerTypes.NSX, ServerTypes.VMC):
                out_formatter.format_output(
                    output.error.get_field('data'),
                    more,
                    self.cmd_info.output_field_list,
                    output_structures_metadata)
                return StatusCode.INVALID_COMMAND
            return StatusCode.INVALID_COMMAND

        return StatusCode.SUCCESS

    def collect_output_structures_metadata(self):
        """
        Collects metadata info for command's output structure types

        :rtype: :class:`list` of
                :class:`vmware.vapi.client.dcli.metadata.metadata_info.StructureInfo`
        :return: List of output structures metadata information
        """
        result = []
        if self.is_cmd:
            for output_info in self.cmd_info.output_field_list:
                if output_info.structure_id != MAP_ENTRY:
                    try:
                        result.append(self.metadata_manager.get_structure_info(
                            output_info.structure_id))
                    except NotFound as e:
                        err_msg = ('No metamodel information found '
                                   'for structure {}').format(output_info.structure_id)
                        handle_error(err_msg, print_error=False)
        return result

    def formatter_apply_structure_filter_visitor(self, struct,
                                                 metadata_struct_info):
        """
        Determines whether a formatter should check whether to print a
        structure field or not.
        Function returns True if there are union tags in the structure,
        False otherwise

        :param struct: data value definition of the structure
        :type struct: :class:`vmware.vapi.data.value.StructValue`
        :param metadata_struct_info: metamodel info of the structure
        :type metadata_struct_info:
           :class:`vmware.vapi.client.dcli.metadata.metadata_info.StructureInfo`
        :return: Whether the structure should be check further for whether to
        print its fields by the formatter
        :rtype: :class:`bool`
        """
        self.current_structure_union_tags = \
            [field for field in struct.get_fields() if
             is_field_union_tag(field[0], metadata_struct_info)]
        return True if self.current_structure_union_tags else False

    def formatter_structure_element_visit(self, field_name, struct,
                                          metadata_struct_info):  # pylint: disable=W0613
        """
        Determines whether a structure field should be printed by the formatter.
        Field gets skiped if it is a union case not active based on the union
        tag it is associated to.

        :param field_name: the strucutre field name
        :type field_name: :class:`str`
        :param struct: data value definition of the structure
        :type struct: :class:`vmware.vapi.data.value.StructValue`
        :param metadata_struct_info: metamodel info of the structure
        :type metadata_struct_info:
           :class:`vmware.vapi.client.dcli.metadata.metadata_info.StructureInfo`
        :return: Whether the field should be printed by the formatter
        :rtype: :class:`bool`
        """
        field_value = struct.get_field(field_name)

        if not metadata_struct_info or \
                not (is_field_union_tag(field_name, metadata_struct_info) or
                     is_field_union_case(field_name, metadata_struct_info)):
            return True
        elif is_field_union_tag(field_name, metadata_struct_info) and \
                (isinstance(field_value, OptionalValue) and
                 field_value.value is None):
            return False
        elif is_field_union_tag(field_name, metadata_struct_info):
            return True

        union_case = get_metadata_field_info(field_name, metadata_struct_info)
        if union_case and \
                union_case_matches_union_tag_value(union_case,
                                                   self.current_structure_union_tags):
            return True
        return False
