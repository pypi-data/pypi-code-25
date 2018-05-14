"""
dcli util classes
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright (c) 2015-2018 VMware, Inc.  All rights reserved. '
__license__ = 'SPDX-License-Identifier: MIT'
__docformat__ = 'epytext en'

import os
import io
import sys
import textwrap
import logging
import time
import json
import re
import six
from Crypto.Cipher import AES
from Crypto import Random
from requests.exceptions import SSLError
from vmware.vapi.data.value import OptionalValue
from vmware.vapi.client.dcli.exceptions import (
    handle_error, handle_ssl_error, extract_error_msg, ParsingExit)
from vmware.vapi.client.dcli import exceptions


class StatusCode(object):
    """
    CLI client status codes
    """
    SUCCESS = 0
    INVALID_COMMAND = 1
    INVALID_ARGUMENT = 2
    INVALID_ENV = 3
    NOT_AUTHENTICATED = 4

    def __init__(self):
        pass


try:
    import argparse
except ImportError as e:
    print('Error: No argparse module present quitting.', file=sys.stderr)
    sys.exit(StatusCode.INVALID_ENV)

try:
    have_pyprompt = True
    import prompt_toolkit  # pylint: disable=W0611
    import pygments  # pylint: disable=W0611
except ImportError:
    have_pyprompt = False

command_exec_report = {}

DCLI_LOGFILE = os.environ.get('DCLI_LOGFILE', '')
DCLI_PROFILE_FILE = os.environ.get('DCLI_PROFILE_FILE', '')
FORMATTERS = ['simple', 'table', 'xml', 'json', 'html', 'csv']
LOGLEVELS = ['debug', 'info', 'warning', 'error']
logger = logging.getLogger(__name__)

UNION_CASE = "UnionCase"
UNION_TAG = "UnionTag"

GET_VMC_ACCESS_TOKEN_PATH = '%s/csp/gateway/am/api/auth/api-tokens/authorize'
VMC_DUMMY_CREDSTORE_USER = 'vmc_user'


class ServerTypes(object):
    """
    Defines server types dcli currently supports
    """
    VSPHERE = 1
    VMC = 2
    NSX = 3


class ArgumentInfo(object):
    """
    ArgumentInfo class to store details of a CLI input argument

    :type  short_name: :class:`str`
    :ivar  short_name: Short name of the CLI command argument
    :type  name: :class:`str`
    :ivar  name: Full name of the CLI command argument
    :type  arg_action: :class:`str`
    :ivar  arg_action: Argument action
    :type  const: :class:`bool`
    :ivar  const: Const or not
    :type  description: :class:`str`
    :ivar  description: Command description
    :type  required: :class:`bool`
    :ivar  required: Required argument or not
    :type  type_: :class:`str`
    :ivar  type_: Argument type
    :type  choices: :class:`tuple`
    :ivar  choices: Possible values for the command argument
    :type  default: :class:`bool`
    :ivar  default: Default value for flag
    :type  nargs: :class:`str`
    :ivar  nargs: nargs for the command argument
    """
    def __init__(self, short_name=None, name=None, arg_action=None, const=None,
                 description=None, required=None, type_=None, choices=None,
                 default=None, nargs=None):
        self.short_name = short_name
        self.name = name
        self.arg_action = arg_action
        self.const = const
        self.description = description
        self.required = required
        self.type_ = type_
        self.choices = choices
        self.default = default
        self.nargs = nargs

    def __str__(self):
        return 'short_name=%s name=%s arg_action=%s const=%s description=%s'\
               'required=%s type=%s choices=%s default=%s nargs=%s'\
               % (self.short_name, self.name, self.arg_action, self.const,
                  self.description, self.required, self.type_, self.choices,
                  self.default, self.nargs)


def get_dcli_dir_path():
    """ Get dcli dir path """
    home = os.path.expanduser('~')
    dcli = '.dcli'
    if home:
        dir_path = os.path.join(home, dcli)
    else:
        logger.error("Unable to find user's home directory")
        raise Exception("Unable to find user's home directory")

    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    return dir_path


def get_dcli_server(server=None, server_type=None):
    """ Get dcli server """
    from six.moves import urllib
    base_url = 'api'
    if server_type == ServerTypes.NSX:
        base_url = 'api/v1'
    elif server_type == ServerTypes.VMC:
        base_url = ''

    result = server

    if not server:
        result = 'http://localhost/%s' % base_url  # Default server url
    else:
        if server.startswith('http'):
            url = urllib.parse.urlparse(server)
            if not url.scheme or not url.netloc:
                logger.error('Invalid server url %s. URL must be of format http(s)://ip:port', server)
                raise Exception('Invalid server url %s. URL must be of format http(s)://ip:port' % server)

            if not url.path or url.path == '/':
                # If only ip and port are provided append /api
                result = '%s://%s/%s' % (url.scheme, url.netloc, base_url)
            else:
                result = server
        else:
            if server_type == ServerTypes.VMC:
                result = 'http://%s/%s' % (server, base_url)
            else:
                result = 'https://%s/%s' % (server, base_url)

    if result.endswith('/'):
        result = result[0:len(result) - 1]

    return result


def init_dcli_options():
    """ Initialize dcli options """
    options = []
    options.append(ArgumentInfo(name='+credstore-add', arg_action='store_true', default=False, description='Store the login credentials in credential store'))
    options.append(ArgumentInfo(name='+credstore-file', arg_action='store', default=DCLI_CREDFILE, description='Specify the dcli credential store file (default: %s)' % DCLI_CREDFILE))
    options.append(ArgumentInfo(name='+credstore-list', arg_action='store_true', default=False, description='List the login credentials stored in credential store'))
    options.append(ArgumentInfo(name='+credstore-remove', arg_action='store_true', default=False, description='Remove the login credentials from credential store'))
    options.append(ArgumentInfo(name='+configuration-file', arg_action='store',
                                default=DCLI_CONFIGFILE,
                                description='Specify the dcli '
                                            'configuration store '
                                            'file (default: %s)' % DCLI_CONFIGFILE))
    options.append(ArgumentInfo(name='+formatter', arg_action='store', choices=FORMATTERS, description='Specify the formatter to use to format the command output'))
    options.append(ArgumentInfo(name='+loglevel', arg_action='store', default='info', choices=LOGLEVELS, description='Specify the log verbosity (default: info)'))
    options.append(ArgumentInfo(name='+more', arg_action='store_true', default=False, description='Flag for page-wise output'))
    options.append(ArgumentInfo(name='+session-manager', arg_action='store', description='Specify the session manager for credential store remove operation'))
    options.append(ArgumentInfo(name='+username', arg_action='store', default=DCLI_USERNAME, description='Specify the username for login (default: %s)' % DCLI_USERNAME))
    options.append(ArgumentInfo(name='+nsx-username', arg_action='store',
                                default=NSX_USERNAME,
                                description='Specify NSX username for login (default: %s)' % NSX_USERNAME))
    return options


DCLI_SERVER = os.environ.get('DCLI_SERVER', get_dcli_server())
NSX_SERVER = os.environ.get('NSX_SERVER', '')
VMC_SERVER = os.environ.get('DCLI_VMC_SERVER', 'https://vmc.vmware.com')
DCLI_USERNAME = os.environ.get('DCLI_USERNAME', '')
NSX_USERNAME = os.environ.get('NSX_USERNAME', '')
DCLI_SSLCERTFILE = os.environ.get('DCLI_SSLCERTFILE', '')
DCLI_SSLKEYFILE = os.environ.get('DCLI_SSLKEYFILE', '')
DCLI_CACERTFILE = os.environ.get('DCLI_CACERTFILE', '')
DCLI_HISTORY_FILE = os.environ.get('DCLI_HISTFILE', os.path.join(
    get_dcli_dir_path(), '.dcli_history'))
DCLI_HISTORY_SIZE = int(os.environ.get('DCLI_HISTSIZE', 500))
DCLI_CREDFILE = os.environ.get('DCLI_CREDFILE', os.path.join(
    get_dcli_dir_path(), '.dcli_credstore'))
DCLI_SHOW_UNRELEASED_APIS = os.environ.get('DCLI_SHOW_UNRELEASED_APIS', 'false').lower() == 'true'
DCLI_CONFIGFILE = os.environ.get('DCLI_CONFIGFILE', os.path.join(
    get_dcli_dir_path(), '.dcli_configuration'))
CLI_CLIENT_NAME = 'dcli'
RPC_PROTOCOL = 'https'
MSG_PROTOCOL = 'json'
DCLI_HISTORY_FILE_PATH = os.path.expanduser(DCLI_HISTORY_FILE)
DCLI_OPTIONS = init_dcli_options()


def get_dcli_hidden_namespaces():
    """
    Helper function to populate DCLI_HIDDEN_NAMESPACES module variable
    :rtype:  :class:`list` of :class:`dict`
    :return: array of dictionaries for the specified namespaces in env variable
    """
    hidden_namespaces = \
        os.environ.get('DCLI_HIDDEN_NAMESPACES', 'com vmware vapi, com vmware vmc model')
    hidden_namespaces = [item.rstrip().lstrip().replace(' ', '.') for item in hidden_namespaces.split(',')]
    for idx, item in enumerate(hidden_namespaces):
        split_item = item.rsplit('.', 1)
        hidden_namespaces[idx] = {'path': split_item[0],
                                  'name': split_item[1] if len(split_item) == 2 else ''}
    return hidden_namespaces


# specify namespaces that should not appear in dcli below (still callable though)
DCLI_HIDDEN_NAMESPACES = get_dcli_hidden_namespaces()


def get_console_size():
    """ Get console height and width """
    # Twisted from ActiveState receipe 440694
    height, width = 25, 80
    import struct
    if os.name == 'nt':
        # Windows
        from ctypes import windll, create_string_buffer

        struct_fmt = "hhhhhhhhhhh"
        buf_size = len(struct_fmt) * 2
        hdl = windll.kernel32.GetStdHandle(-12)
        screen_buf_inf = create_string_buffer(buf_size)
        ret = windll.kernel32.GetConsoleScreenBufferInfo(hdl, screen_buf_inf)

        if ret:
            (_, _, _, _, _, sr_windows_left, sr_windows_top,
             sr_windows_right, sr_windows_bottom, _, _) = struct.unpack(struct_fmt, screen_buf_inf.raw)
            width = sr_windows_right - sr_windows_left + 1
            height = sr_windows_bottom - sr_windows_top + 1
    else:
        # Posix
        import fcntl
        import termios
        tio_get_windows_size = struct.pack(str("HHHH"), 0, 0, 0, 0)
        try:
            ret = fcntl.ioctl(1, termios.TIOCGWINSZ, tio_get_windows_size)
        except Exception:
            logger.warning('ioctl to determine console size failed')
            return height, width
        height, width = struct.unpack("HHHH", ret)[:2]

    if height > 0 and width > 0:
        return height, width
    return 25, 80


def get_wrapped_text(text, width):
    """
    Word wrap a given text based upon given width

    :type  text: :class:`str`
    :param text: Text to be word wrapped
    :type  width: :class:`int`
    :param width: Width to be word wrapped to

    :rtype:  :class:`list` of :class:`str`
    :return: List of word wrapped strings
    """
    wrapper = textwrap.TextWrapper(width=width)
    return wrapper.wrap(text)


def print_top_level_help(interactive_mode=False):
    """
    Print the top level dcli help

    :type interactive_mode: :class:`bool`
    :param interactive_mode: Specifies whether dcli is in interactive mode or not
    """
    print('Welcome to VMware Datacenter CLI (DCLI)')
    print()
    if not interactive_mode:
        print('usage:', CLI_CLIENT_NAME, '<namespaces> <command>')
        print()
        print('To enter interactive shell mode:', CLI_CLIENT_NAME, '+interactive')
        print('To specify an alternate server:', CLI_CLIENT_NAME, '+server <server>')
        print('To specify default values for specific options: env options')
        print('For detailed help please use:', CLI_CLIENT_NAME, '--help')
    else:
        print('usage:', '<namespaces> <command>')
        print()
        print('To auto-complete and browse DCLI namespaces:   <TAB>')
        print('If you need more help for a command:           vcenter vm get --help')
        print('If you need more help for a namespace:         vcenter vm --help')
        print('To specify default values for specific options: env options')
        print('For detailed information on DCLI usage visit:  http://vmware.com/go/dcli')


saved_user_pass = (None, None, False)


def prompt_for_user_and_password(server_type, clear_context=False):
    """
    Prompts user for credentials

    :type server_type: :class:`int`
    :param server_type: server type to give string value for

    :return: prompted username, password, and whether credentials should
        be stored in credstore
    """
    global saved_user_pass  # pylint: disable=W0603

    if not clear_context and saved_user_pass != (None, None, False):
        return saved_user_pass

    username = None
    password = None

    try:
        # For Python 3 compatibility
        input_func = raw_input  # pylint: disable=W0622
    except NameError:
        input_func = input

    import getpass
    if server_type == ServerTypes.VMC:
        username = VMC_DUMMY_CREDSTORE_USER
        password = getpass.getpass(str('Refresh Token: ')).strip()
    else:
        username = input_func('Username: ')
        password = getpass.getpass(str('Password: '))

    credstore_flag = False
    if server_type == ServerTypes.VMC:
        credstore_answer = \
            input_func('Do you want to save refresh token in the '
                       'credstore? (y or n) [y]:')
    else:
        credstore_answer = \
            input_func('Do you want to save credentials in the '
                       'credstore? (y or n) [y]:')
    if credstore_answer.lower().strip() in ['', 'true', 'yes', 'y', 't']:
        credstore_flag = True

    saved_user_pass = username, password, credstore_flag

    return username, password, credstore_flag


def derive_key_and_iv(password, salt, key_length, iv_length):
    """
    Get key and initialization vector for AES encryption

    :type   password: :class:`str`
    :param  password: Password used for encryption
    :type   salt: :class:`str`
    :param  salt: Encryption salt
    :type   key_length: :class:`str`
    :param  key_length: Encryption key length
    :type   iv_length: :class:`str`
    :param  iv_length: IV length

    :rtype:  :class:`str`
    :return: Encryption Key
    :rtype:  :class:`str`
    :return: Initialization Vector
    """
    d = d_i = ''
    from hashlib import md5
    while len(d) < key_length + iv_length:
        d_i = md5(d_i.encode() + password.encode() + salt).hexdigest()
        d += d_i
    return d[:key_length], d[key_length:key_length + iv_length]


def encrypt(input_pwd, password, key_length=32):
    """
    Method to encrypt password

    :type   input_pwd: :class:`str`
    :param  input_pwd: Password to be encrypted
    :type   password: :class:`str`
    :param  password: Password used to do encryption
    :type   key_length: :class:`int`
    :param  key_length: Encryption key length

    :rtype: :class:`str`
    :return: Base64 encoded encrypted password
    """
    bs = AES.block_size
    salt = Random.new().read(bs - len('Salted__'))
    key, iv = derive_key_and_iv(password, salt, key_length, bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Add padding if input password is not multiple of block size
    if not input_pwd or len(input_pwd) % bs != 0:
        padding_length = (bs - len(input_pwd) % bs) or bs
        input_pwd += padding_length * chr(padding_length)
    encrypted = b'Salted__' + salt + cipher.encrypt(input_pwd)
    import base64
    return (base64.encodestring(encrypted) if six.PY2 else  # pylint: disable=W1505
            base64.encodebytes(encrypted))  # pylint: disable=E1101,W1505


def decrypt(encoded_pwd, password, key_length=32):
    """
    Method to decrypt password

    :type   encoded_pwd: :class:`str`
    :param  encoded_pwd: Password to be decrypted
    :type   password: :class:`str`
    :param  password: Password used to do encryption
    :type   key_length: :class:`int`
    :param  key_length: Encryption key length

    :rtype: :class:`str`
    :return: Decrypted password
    """
    import base64
    if six.PY3 and not isinstance(encoded_pwd, bytes):
        encoded_pwd = encoded_pwd.encode()
    encoded_pwd = base64.decodestring(encoded_pwd)  # pylint: disable=W1505
    bs = AES.block_size
    salt = encoded_pwd[:bs][len('Salted__'):]
    key, iv = derive_key_and_iv(password, salt, key_length, bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    pwd = cipher.decrypt(encoded_pwd[bs:])
    # return password after removing padding
    result = ''
    if six.PY3:
        result = pwd.rstrip(chr(pwd[-1]).encode()).decode()
    else:
        result = pwd.rstrip(pwd[-1])
    return result


def calculate_time(fn, info, command=None):
    """
    Helper function to measure execution time of a function

    :param fn: function to execute
    :type fn: :class:`function`
    :param info: short information for the executable function
    :type info: :class:`str`
    :param command: dcli command currently executed.
    If none the measurement result is appended to the last command added.
    :type command: :class:`str`
    :return: Actual result from the :param fn: function
    :rtype: :class:`object`
    """
    if DCLI_PROFILE_FILE:
        if command:
            if 'command' not in command_exec_report:
                command_exec_report['command'] = command
                report_item = command_exec_report
            elif command_exec_report['command'] == command:
                report_item = command_exec_report
            else:
                report_item = {'command': command}
                command_exec_report.setdefault('shell_commands', []).append(report_item)
        else:
            if 'shell_commands' in command_exec_report:
                report_item = command_exec_report['shell_commands'][-1]
            else:
                report_item = command_exec_report

        measurement = {'info': info}

        # to ensure report tree has correct hierarchical structure
        # add measurement to the right most node of report tree which has no time_taken filled yet.
        while 'measurements' in report_item and report_item['measurements']:
            if 'time_taken' in report_item['measurements'][-1]:
                break
            report_item = report_item['measurements'][-1]
        report_item.setdefault('measurements', []).append(measurement)

        start_time = time.time()
        result = fn()
        execution_time = time.time() - start_time

        measurement['time_taken'] = '{0:2f}sec'.format(execution_time)
    else:
        result = fn()

    return result


def save_report_to_file():
    """
    Saves dcli commands execution report
    to the file specified by DCLI_PROFILE_FILE env variable

    :return:
    :rtype: None
    """
    if DCLI_PROFILE_FILE:
        with io.open(DCLI_PROFILE_FILE, 'a', encoding='utf-8') as times_file:
            val = json.dumps(command_exec_report, indent=4, sort_keys=True)
            result = six.text_type(val if times_file.tell() == 0 else ',' + val)
            times_file.write(result)


def is_field_union_tag(field_name, metadata_struct_info):
    """
    Checks whether a given structure field name is found in a structure and is
    a union tag

    :param field_name: field name of the structure's member
    :type field_name: :class:`str`
    :param metadata_struct_info: metadata info of the structure to check
        against
    :type metadata_struct_info:
        :class:`vmware.vapi.client.dcli.metadata.metadata_info.StructureInfo`
    :return: True if given field_name is union tag, False otherwise
    :rtype: :class:`bool`
    """
    if not metadata_struct_info:
        return False
    return next((True for mm_field in metadata_struct_info.fields
                 if mm_field.name == field_name and mm_field.is_union_tag()), False)


def is_field_union_case(field_name, metadata_struct_info):
    """
    Checks whether a given structure field name is found in a structure and is
    a union case

    :param field_name: field name of the structure's member
    :type field_name: :class:`str`
    :param metadata_struct_info: metadata info of the structure to check
        against
    :type metadata_struct_info:
        :class:`vmware.vapi.client.dcli.metadata.metadata_info.StructureInfo`
    :return: True if given field_name is union case, False otherwise
    :rtype: :class:`bool`
    """
    if not metadata_struct_info:
        return False
    return next((True for mm_field in metadata_struct_info.fields
                 if mm_field.name == field_name and mm_field.is_union_case()), False)


def get_metadata_field_info(field_name, metadata_struct_info):
    """
    Get metamodel information for a field

    :param field_name: field name of the structure's member
    :type field_name: :class:`str`
    :param metadata_struct_info: metamodel info of the structure
    :type metadata_struct_info:
        :class:`com.vmware.vapi.metadata.metamodel_client.StructureInfo`
    :return: Metamodel representation object
    :rtype: :class:`com.vmware.vapi.metadata.metamodel_client.FieldInfo`
    """
    return next((mm_field for mm_field in metadata_struct_info.fields
                 if mm_field.name == field_name), None)


def union_case_matches_union_tag_value(union_field_info, union_tags):
    """
    Verifies whether a union case field should be visible based on a union tag

    :param union_field_info: metamodel presentation of the union case
    :type union_field_info: :class:`com.vmware.vapi.metadata.metamodel_client
                                                            .FieldInfo`
    :param union_tags: datavalue presentation of the union tags
    :type union_tags: :class: class:`list` of :class:`tuple`
    :return: True if UnionCase field matches UnionTag value
    :rtype: :class:`bool`
    """
    if not union_field_info.is_union_case():
        err_msg = 'Invalid union field value found.'
        handle_error(err_msg)
        return False

    for tag_name, tag_value in union_tags:
        if isinstance(tag_value, OptionalValue):
            if tag_value.value is None:
                return False
            tag_value = tag_value.value
        if tag_name != union_field_info.union_case.tag_name:
            continue
        for union_case_value in union_field_info.union_case.list_value:
            if tag_value.value == union_case_value:
                return True
    return False


def get_vmc_authentication_token(session, refresh_token=None):
    """
    Fetches VMC authentication token

    :param session: requests session object which would make the http requests
    :type session: :class: `requests.sessions.Session`
    :return: VMC token
    :rtype: :class:`str`
    """
    # get CSP server uri
    token = None
    csp_uri = os.getenv('DCLI_VMC_CSP_URL', 'https://console.cloud.vmware.com')
    if not csp_uri:
        error_msg = ('Please set DCLI_VMC_CSP_URL environment variable to '
                     'valid CSP service URL.')
        handle_error(error_msg)
        raise Exception(error_msg)
    logger.info('Using CSP address "%s"', csp_uri)

    if not refresh_token:
        error_msg = ('No refresh token provided. Provide a '
                     'valid refresh token for authentication to VMC '
                     'when prompted')
        handle_error(error_msg)
        raise Exception(error_msg)
    try:
        # striping last / so that the user provided url with
        # or without it would be valid
        csp_uri = csp_uri.strip().rstrip('/')  # triming last slash and any whitespaces
        request_url = GET_VMC_ACCESS_TOKEN_PATH % csp_uri
        data = "refresh_token=%s" % refresh_token.strip()  # removing any whitespaces before or after refresh token
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        logger.info('Making request for getting csp token to "%s"', request_url)
        token_response = session.post(request_url,
                                      data=data,
                                      headers=headers)
        token = token_response.json()['access_token']
    except SSLError as e:
        handle_ssl_error(e)
    except Exception as e:
        error_msg = ('Unable to obtain VMC authentication token. '
                     'Using CSP login address: %s (override using DCLI_VMC_CSP_URL env var). '
                     'Are you sure you have provided correct refresh token?\r\n'
                     'Error: %s' % (csp_uri, str(e)))
        handle_error(error_msg)
        raise e
    return token


class DcliContext(object):
    """
    Class used to collect dcli context
    """
    def __init__(self, **kwargs):
        self.configuration_path = kwargs.get('configuration_path')
        self.server = kwargs.get('server')
        self.server_type = kwargs.get('server_type')


class CliGenericTypes(object):
    """
    Defines dcli recognized generic types
    """
    list_type = 'list'
    optional_type = 'optional'
    optional_list_type = 'optional_list'
    list_of_optional_type = 'list_optional'
    none_type = ''


class TypeInfoGenericTypes(object):
    """
    Defines generic types used by
    :class:`com.vmware.vapi.client.dcli.metadata.metadata_info.TypeInfo`
    """
    optional_type = 'optional'
    list_type = 'list'
    set_type = 'set'
    map_type = 'map'


class ParsingError(RuntimeError):
    """
    Class to extend RuntimeError class
    """
    def __init__(self, msg):
        RuntimeError.__init__(self, msg)
        self.msg = msg


class CliArgParser(argparse.ArgumentParser):
    """
    Class to catch argparse errors
    """
    def error(self, message):
        """
        Extend argparse error method
        """
        raise ParsingError(message)

    def exit(self, status=0, message=None):
        """
        Extend argparse exit method
        """
        raise ParsingExit(status, message)


class CliHelpFormatter(argparse.HelpFormatter):
    """
    Class to define dcli help formatter to use screen width for help
    """
    def __init__(self,
                 prog,
                 width=None):
        _, width = get_console_size()
        argparse.HelpFormatter.__init__(self, prog, width=width)
        return


class BoolAction(argparse.Action):
    """
    Class to define boolean argparse action
    """
    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,   # pylint: disable=W0622
                 choices=None,
                 required=False,
                 help=None,  # pylint: disable=W0622
                 metavar=None):
        argparse.Action.__init__(self,
                                 option_strings=option_strings,
                                 dest=dest,
                                 nargs=nargs,
                                 const=const,
                                 default=default,
                                 type=type,
                                 choices=choices,
                                 required=required,
                                 help=help,
                                 metavar=metavar)
        return

    def __call__(self, parser, namespace, values, option_string=None):
        values = CliHelper.str_to_bool(values)
        setattr(namespace, self.dest, values)


class BoolAppendAction(argparse.Action):
    """
    Class to define boolean argparse append action
    """
    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,   # pylint: disable=W0622
                 choices=None,
                 required=False,
                 help=None,  # pylint: disable=W0622
                 metavar=None):
        argparse.Action.__init__(self,
                                 option_strings=option_strings,
                                 dest=dest,
                                 nargs=nargs,
                                 const=const,
                                 default=default,
                                 type=type,
                                 choices=choices,
                                 required=required,
                                 help=help,
                                 metavar=metavar)
        return

    def __call__(self, parser, namespace, values, option_string=None):
        values = CliHelper.str_to_bool(values)

        if getattr(namespace, self.dest) is None:
            setattr(namespace, self.dest, [])
        items = getattr(namespace, self.dest)
        items.append(values)
        setattr(namespace, self.dest, items)


class CliHelper(object):
    """
    CLI helper class to provide various helper functions for CLI client
    """
    def __init__(self):
        pass

    @staticmethod
    def get_parser(interactive):
        """
        Get the CliArgParser object with all input vcli arguments configured

        :type: :class:`bool`
        :param: Flag if we are in interactive mode or not

        :rtype:  :class:`CliArgParser`
        :return: CliArgParser object
        """
        parser = CliArgParser(prog=CLI_CLIENT_NAME,
                              prefix_chars='+',
                              description='VMware Datacenter Command Line Interface',
                              formatter_class=CliHelpFormatter,
                              add_help=False)
        if not interactive:
            server_mutex_group = parser.add_mutually_exclusive_group()
            server_mutex_group.add_argument('+server',
                                            action='store',
                                            default=DCLI_SERVER,
                                            help='Specify VAPI Server IP '
                                                 'address/DNS name (default: %(default)s)')
            server_mutex_group.add_argument('+nsx-server',
                                            action='store',
                                            default=NSX_SERVER,
                                            help='Specify NSX Server IP '
                                                 'address/DNS name (default: %(default)s)')
            server_mutex_group.add_argument('+vmc-server',
                                            nargs='?',
                                            const=VMC_SERVER,
                                            action='store',
                                            help='Specify VMC Server IP '
                                                 'address/DNS name (default: %(default)s)')

            if have_pyprompt:  # Only show these options if pyprompt is present
                parser.add_argument('+interactive', action='store_true', default=False, help='Open a CLI shell to invoke commands')
                parser.add_argument('+prompt', action='store', default='%s> ' % CLI_CLIENT_NAME, help='Prompt for cli shell (default: %(default)s)')

            ssl_mutex_group = parser.add_mutually_exclusive_group()
            ssl_mutex_group.add_argument('+skip-server-verification', action='store_true', default=False, help='Skip server SSL verification process (default: %(default)s)')
            ssl_mutex_group.add_argument('+cacert-file', action='store', default=DCLI_CACERTFILE, help='Specify the certificate authority certificates for validating SSL connections (format: PEM) (default: %(default)s)')

            # To show commands and namepaces of APIs that are under development
            parser.add_argument('+show-unreleased-apis',
                                action='store_true',
                                default=DCLI_SHOW_UNRELEASED_APIS,
                                help=argparse.SUPPRESS)

        password_mutex_group = parser.add_mutually_exclusive_group()
        # removing help=argparse.SUPPRESS from params bellow due to issue
        # https://bugs.python.org/issue22363
        password_mutex_group.add_argument('+password',
                                          action='store_true',
                                          default=False)
        password_mutex_group.add_argument('+nsx-password',
                                          action='store_true',
                                          default=False)

        mutex_group = parser.add_mutually_exclusive_group()
        username_mutext_group = parser.add_mutually_exclusive_group()
        for option in DCLI_OPTIONS:
            kwargs = {
                'action': option.arg_action,
                'help': option.description,
            }

            if option.choices:
                kwargs['choices'] = option.choices
            if option.default is not None:
                kwargs['default'] = option.default
            if option.name.startswith('+credstore'):
                mutex_group.add_argument(option.name, **kwargs)
            elif option.name.startswith('+username'):
                username_mutext_group.add_argument(option.name, **kwargs)
            else:
                parser.add_argument(option.name, **kwargs)
        parser.add_argument('args', nargs='*', help='CLI command')

        return parser

    @staticmethod
    def str_to_bool(value):
        """
        Method to convert a string to boolean type
        """
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        else:
            raise ParsingError("Invalid boolean value '%s' specified" % value)

    @staticmethod
    def strip_quotes(value):
        """
        Method to strip quotes from start and end of a string
        """
        return value.lstrip('"').rstrip('"').lstrip("'").rstrip("'")

    @staticmethod
    def get_cli_args(command):
        """
        Method to convert tokens into cli-friendly args
        """
        # XXX Revisit this tokenizer logic to be more robust

        tokens = re.split(r'\s', command)
        arg_list = []
        prev = ''
        in_word = False
        for token in tokens:
            if in_word:
                prev += ' %s' % token
                if token.endswith('"') or token.endswith("'"):
                    arg_list.append(prev)
                    prev = ''
                    in_word = False
            elif token.startswith('"') or token.startswith("'"):
                prev += token
                if token.endswith('"') or token.endswith("'"):
                    arg_list.append(prev)
                    prev = ''
                else:
                    in_word = True
            elif token:
                arg_list.append(token)

        return [CliHelper.strip_quotes(arg) for arg in arg_list]

    @staticmethod
    def convert_vapi_to_python_type(type_str):
        """
        Convert the vapi type name to python type name

        :type  type_str: :class:`str`
        :param type_str: vAPI type name

        :rtype:  :class:`type`
        :return: Python type name
        """
        return {'long': int,
                'boolean': bool,
                'double': float}.get(type_str, six.text_type)

    @staticmethod
    def get_command_path(args):
        """
        Break the argument list into command path and name

        :type  args: :class:`list` of :class:`str`
        :param args: vCLI command argument list

        :rtype:  :class:`list` of :class:`str` and :class:`str`
        :return: Command path and name
        """
        if args:
            path = '.'.join(args[:-1])
            name = args[-1]
        else:
            path = ''
            name = ''
        return path, name

    @staticmethod
    def prompt_for_secret(prompt):
        """
        Provide non-echo prompt for secret fields

        :type  prompt: :class:`str`
        :param prompt: Prompt for secret input

        :rtype:  :class:`str`
        :return: Secret value
        """
        try:
            import getpass
            secret = getpass.getpass(str(prompt))
            return secret
        except (EOFError, KeyboardInterrupt):
            pass

        # XXX change to return
        sys.exit(StatusCode.INVALID_ARGUMENT)

    @staticmethod
    def process_input(parser, input_args, cli_main, is_interactive, shell, credstore, fp=sys.stdout):
        """
        Method to split input arguments into vapi and dcli arguments and execute command

        :type  parser: :class:`CliArgParser`
        :param parser: CliArgParser object
        :type  input_args: :class:`list` of input argument options
        :param input_args: Input arguments list
        :type  cli_main: :class:`CliMain`
        :param cli_main: CliMain object
        :type  is_interactive: :class:`bool`
        :param is_interactive: Is in interactive mode
        :type  shell: :class:`CliShell`
        :param shell: CliShell object
        :type  credstore: :class:`CredStore`
        :param credstore: CredStore object

        :rtype:  :class:`StatusCode`
        :return: StatusCode
        """
        cli_client_args = input_args[0]

        cmd_args = list(sys.argv[1:])

        if cli_client_args.args and \
                (cli_client_args.args[0] == '-h' or
                 cli_client_args.args[0] == '--help'):
            parser.print_help()
            return StatusCode.SUCCESS

        server, username, password, server_type = \
            CliHelper.get_common_params(cli_client_args, is_interactive)

        if (username or password) and server_type == ServerTypes.VMC:
            handle_error('When connected to VMC server you need to provide '
                         'refresh token instead of username/password '
                         'credentials. You can do this when prompted.')
            return StatusCode.INVALID_ARGUMENT

        if password and not username:
            handle_error('Missing username argument')
            return StatusCode.NOT_AUTHENTICATED

        if (cli_client_args.session_manager and
                not cli_client_args.credstore_remove):
            handle_error('session-manager option only available with credstore-remove option')
            return StatusCode.INVALID_ARGUMENT

        if CliHelper.should_prompt_for_secret(username,
                                              password,
                                              cli_client_args,
                                              is_interactive):
            password = CliHelper.prompt_for_secret('Password: ')

        if cli_client_args.credstore_list:
            credstore.set_credstore_path(cli_client_args.credstore_file)
            return credstore.list(cli_client_args.formatter)

        if cli_client_args.credstore_remove:
            logger.info('Removing credstore entry')
            credstore.set_credstore_path(cli_client_args.credstore_file)
            return credstore.remove(cli_main.server
                                    if cli_main.server else server,
                                    username, cli_client_args.session_manager)

        if not is_interactive:
            try:
                cli_main.init_main(rpc=RPC_PROTOCOL,
                                   msg_protocol=MSG_PROTOCOL,
                                   server=server,
                                   server_type=server_type,
                                   username=username,
                                   password=password,
                                   credstore_file=cli_client_args.credstore_file,
                                   credstore_add=cli_client_args.credstore_add,
                                   configuration_file=cli_client_args.configuration_file,
                                   skip_server_verification=cli_client_args.skip_server_verification,
                                   cacert_file=cli_client_args.cacert_file,
                                   show_unreleased_apis=cli_client_args.show_unreleased_apis,
                                   more=cli_client_args.more)
                CliHelper.log_command_securely(input_args, cmd_args, cli_main)
            except Exception as e:
                msg = extract_error_msg(e)
                handle_error(msg, print_usage=True)
                return StatusCode.INVALID_ARGUMENT
            if have_pyprompt and cli_client_args.interactive:
                cli_main.interactive = True
                if username and password:
                    cli_main.i_username = username
                    cli_main.i_password = encrypt(password, cli_main.server + cli_main.username)

                try:
                    calculate_time(lambda: shell.init_cache(cli_main,
                                                            cli_client_args.prompt),
                                   'initialize shell cache')
                except Exception as e:
                    msg = extract_error_msg(e)
                    handle_error(msg, print_usage=True)
                    return StatusCode.INVALID_ARGUMENT

                logger.info('Starting interactive mode')
                shell.invoke_shell()
                logger.info('Doing session logout from session manager')
                cli_main.session_logout()
                return StatusCode.SUCCESS
        else:  # Interactive mode options
            if username and not(DCLI_USERNAME and DCLI_USERNAME == username):
                cli_main.username = username.encode('utf-8') \
                    if six.PY2 else str(username)
            cli_main.more = cli_client_args.more
            cli_main.password = password
            cli_main.credstore_file = cli_client_args.credstore_file.encode('utf-8') \
                if six.PY2 else str(cli_client_args.credstore_file)
            cli_main.configuration_file = cli_client_args.configuration_file.encode('utf-8') \
                if six.PY2 else str(cli_client_args.configuration_file)
            cli_main.credstore_add = cli_client_args.credstore_add

        arg_list = cli_client_args.args + input_args[1]
        vapi_cmd, vapi_cmd_args = CliHelper.break_command_from_args(arg_list)

        status = CliHelper.handle_vcli_input(cli_main,
                                             vapi_cmd,
                                             vapi_cmd_args,
                                             cli_client_args.formatter,
                                             fp)

        logger.info('Doing session logout from session manager')
        calculate_time(cli_main.session_logout, 'session logout time')
        return status

    @staticmethod
    def break_command_from_args(args_list):
        """
        Splits given args into cmd args and options args
        """
        # break command path and args
        if args_list:
            arg_index = [i for i, x in enumerate(args_list) if x.startswith('-')]
            index = len(args_list) if not arg_index else arg_index[0]
            cmd = args_list[0:index]
            cmd_args = args_list[index:]
        else:
            cmd = ''
            cmd_args = None
        return cmd, cmd_args

    @staticmethod
    def should_prompt_for_secret(username, password, cli_client_args,
                                 is_interactive):
        """
        Verifies whether dcli should prompt for password

        :type  cli_client_args: :class:`list` of input argument options
        :param cli_client_args: Input arguments list
        :type  is_interactive: :class:`bool`
        :param is_interactive: Is in interactive mode

        :rtype:  :class:`bool`
        :return: True or False depending on whether user should be prompted for password
        """
        result = False
        if password or (username and not cli_client_args.credstore_remove):
            result = True

        if is_interactive and DCLI_USERNAME and username == DCLI_USERNAME:
            result = False

        return result

    @staticmethod
    def get_common_params(cli_client_args, is_interactive):
        """
        Tries to get correct credential and server values depending on how
        they were entered by the user

        :type cli_client_args:
        :param cli_client_args:
        :type is_interactive: :class:`bool`
        :param is_interactive: Is in interactive mode

        :rtype: :class:`tuple` of :class:`str`, :class:`str`, :class:`str`,
        and :class:`str`,
        :return: server, username, password, and connection type as entered
        by the user
        """
        server = None
        server_type = None

        if not is_interactive:
            if cli_client_args.nsx_server:
                server = get_dcli_server(cli_client_args.nsx_server,
                                         server_type=ServerTypes.NSX)
                server_type = ServerTypes.NSX
            elif cli_client_args.vmc_server:
                server = get_dcli_server(cli_client_args.vmc_server,
                                         server_type=ServerTypes.VMC)
                server_type = ServerTypes.VMC
            else:
                server = get_dcli_server(cli_client_args.server)
                server_type = ServerTypes.VSPHERE

        if cli_client_args.nsx_username:
            username = cli_client_args.nsx_username
        else:
            username = cli_client_args.username

        if cli_client_args.nsx_password:
            password = cli_client_args.nsx_password
        else:
            password = cli_client_args.password

        return server, username, password, server_type

    @staticmethod
    def get_module_name(server_type):
        """
        gives string value for specified server type

        :type server_type: :class:`int`
        :param server_type: server type to give string value for
        :rtype: :class:`str`
        :return: string representation of module name
        """
        if server_type == ServerTypes.VMC:
            return 'vmc'
        elif server_type == ServerTypes.NSX:
            return 'nsx'
        elif server_type == ServerTypes.VSPHERE:
            return 'vsphere'
        else:
            raise Exception('No module found for provided server_type')

    @staticmethod
    def handle_vcli_input(cli_main, vapi_cmd, vapi_cmd_args, formatter, fp):
        """
        Method to handle vcli input arguments

        :type  cli_main: :class:`CliMain`
        :param cli_main: CliMain object
        :type  vapi_cmd: :class:`list` of vAPI command split path
        :param vapi_cmd: vAPI command
        :type  vapi_cmd_args: :class:`list` of vAPI command input argument options
        :param vapi_cmd_args: vAPI command input arguments list
        :type  formatter: :class:`str`
        :param formatter: Formatter

        :rtype:  :class:`StatusCode`
        :return: Status code
        """
        if not vapi_cmd:
            if vapi_cmd_args:
                error_msg = 'unrecognized arguments: %s' % ' '.join(vapi_cmd_args)
                handle_error(error_msg)
                return StatusCode.INVALID_COMMAND
            status = cli_main.handle_command('', '', 'table')
        else:
            status = cli_main.handle_command(vapi_cmd, vapi_cmd_args, formatter, fp)

        return status

    @staticmethod
    def configure_logging(log_level):
        """
        Method to configure dcli logging
        """
        file_path = os.devnull
        if not DCLI_LOGFILE:
            if os.name == 'nt':
                home_env = 'APPDATA'
                home = os.environ.get(home_env)
                if os.access(home, os.W_OK):
                    dir_path = os.path.join(home, 'VMware', 'vapi')
                    if not os.path.isdir(dir_path):
                        os.makedirs(dir_path)
                    file_path = os.path.join(dir_path, 'dcli.log')
            else:
                dir_path = '/var/log/vmware/vapi'
                if os.access('/', os.W_OK):
                    if not os.path.isdir(dir_path):
                        os.makedirs(dir_path)
                    file_path = '%s/dcli.log' % (dir_path)
        else:
            file_path = DCLI_LOGFILE

        if log_level == 'debug':
            log_level = logging.DEBUG
        elif log_level == 'info':
            log_level = logging.INFO
        elif log_level == 'warning':
            log_level = logging.WARNING
        elif log_level == 'error':
            log_level = logging.ERROR
        elif log_level == 'critical':
            log_level = logging.CRITICAL

        handler = logging.FileHandler(file_path)
        handler.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(name)-15s %(message)s')
        handler.setFormatter(formatter)
        # Configure the root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.addHandler(handler)

        if log_level == logging.DEBUG:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.name = 'console_handler'
            console_handler.setLevel(log_level)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        else:
            remove_handlers = [handler for handler in root_logger.handlers
                               if handler.name == 'console_handler']
            for handler in remove_handlers:
                root_logger.removeHandler(handler)

        global logger  # pylint: disable=W0603
        logger = logging.getLogger('vmware.vapi.client.dcli.util')

    @staticmethod
    def get_command_secret_map(input_args, cli_main):
        """
        From given input arguments returns whether they form dcli command,
        and the secret map for it
        """
        result = False, None
        old_ignore_error = exceptions.ignore_error
        exceptions.ignore_error = True
        try:
            cmd, _ = CliHelper.break_command_from_args(input_args)
            path, name = CliHelper.get_command_path(cmd)
            cli_cmd_instance = cli_main.get_cmd_instance(path, name)
            if cli_cmd_instance.is_a_command():
                if cli_cmd_instance.secret_map is None:
                    cli_cmd_instance.get_parser_arguments()
                result = True, cli_cmd_instance.secret_map
        finally:
            exceptions.ignore_error = old_ignore_error
        return result

    @staticmethod
    def represents_number(val):
        """
        Verifies whether a given string represents a number (float or integer)
        """
        try:
            float(val)
            return True
        except ValueError:
            return False

    @staticmethod
    def get_secure_command(all_args, dcli_cmd_str, cli_main, substitute='*****'):
        """
        From given command string produces new one with escaped values for
        secure options
        """
        arg_list = dcli_cmd_str.split()
        is_command, secret_map = CliHelper.get_command_secret_map(arg_list, cli_main)
        if is_command and secret_map:
            next_is_secure = False
            secured_args = []
            for i, arg in enumerate(all_args):
                if next_is_secure:
                    if substitute != '':
                        secured_args.append(substitute)
                else:
                    secured_args.append(arg)

                next_is_secure = \
                    bool(
                        len(all_args) > i + 1 and
                        arg.startswith('-') and
                        not CliHelper.represents_number(arg) and
                        arg.lstrip('-') in secret_map and
                        not (all_args[i + 1].startswith('--') or
                             all_args[i + 1].startswith('+') or
                             (all_args[i + 1].startswith('-') and
                              not CliHelper.represents_number(all_args[i + 1])))
                    )

            dcli_cmd_str = ' '.join(secured_args)
        else:
            dcli_cmd_str = ' '.join(all_args)

        return dcli_cmd_str

    @staticmethod
    def log_command_securely(parser_args, all_input_args, cli_main):
        """
        Logs command which starts dcli securely without
        exposing actual dcli command which might contain secret values
        """
        if six.PY2:
            input_ = [i.decode('utf-8') for i in all_input_args]
        else:
            input_ = all_input_args

        if parser_args[0].args or parser_args[1]:
            dcli_command_args = parser_args[0].args + parser_args[1]
            is_command, secret_map = CliHelper.get_command_secret_map(dcli_command_args, cli_main)
            if is_command and secret_map:
                secure_cmd = CliHelper.get_secure_command(input_, ' '.join(dcli_command_args), cli_main)
            else:
                secure_cmd = ' '.join(input_)
        else:
            secure_cmd = ' '.join(input_)

        logger.info('Running command: dcli %s', secure_cmd)
