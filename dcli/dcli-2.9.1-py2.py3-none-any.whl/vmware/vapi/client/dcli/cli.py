#!/usr/bin/env python
"""
CLI client
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright (c) 2015-2018 VMware, Inc.  All rights reserved. '
__license__ = 'SPDX-License-Identifier: MIT'
__docformat__ = 'epytext en'

import logging
import os
import sys
import uuid
import six
import requests

from com.vmware.vapi.std.errors_client import NotFound
from vmware.vapi.lib import connect
from vmware.vapi.client.dcli.metadata.metadata_manager import MetadataManager
from vmware.vapi.client.dcli.metadata.remote_metadata_provider import \
    RemoteMetadataProvider
from vmware.vapi.client.dcli.metadata.local_metadata_provider import \
    LocalMetadataProvider
from vmware.vapi.client.lib.formatter import Formatter
from vmware.vapi.client.dcli.shell import CliShell
from vmware.vapi.client.dcli.credstore import CredStore
from vmware.vapi.client.dcli.namespace import CliNamespace
from vmware.vapi.client.dcli.command import CliCommand
from vmware.vapi.client.dcli.util import (
    CliHelper, StatusCode, ParsingError,
    have_pyprompt, encrypt, decrypt, calculate_time, save_report_to_file,
    ServerTypes, get_vmc_authentication_token, DcliContext,
    prompt_for_user_and_password)
from vmware.vapi.client.dcli.exceptions import handle_error, \
    extract_error_msg, handle_server_error, ParsingExit
from vmware.vapi.core import ApplicationContext
from vmware.vapi.lib.constants import (OPID, SHOW_UNRELEASED_APIS)
from vmware.vapi.security.session import create_session_security_context
from vmware.vapi.security.sso import (create_saml_bearer_security_context,
                                      SAML_BEARER_SCHEME_ID)
from vmware.vapi.security.user_password import (
    create_user_password_security_context, USER_PASSWORD_SCHEME_ID)
from vmware.vapi.security.oauth import create_oauth_security_context
from vmware.vapi.client.dcli.internal_commands.options import Options

# Change terminal to handle readline issue of displaying weird characters
os.environ['TERM'] = 'vt100'


"""
Disable the InsecurePlatform warning due to the use of Python 2.7 that has
older version of ssl compiled with it
"""  # pylint: disable=W0105
try:
    requests.packages.urllib3.disable_warnings()  # pylint: disable=E1101
except AttributeError:
    # Not present in older versions of requests so ignore the error
    pass

USER_PASS_RETRY_LIMIT = 1

NO_AUTHN_SCHEME = 'com.vmware.vapi.std.security.no_authentication'
SERVER_UNAUTHENTICATED_ERROR = 'com.vmware.vapi.std.errors.unauthenticated'
SERVER_UNAUTHORIZED_ERROR = 'com.vmware.vapi.std.errors.unauthorized'
logger = logging.getLogger(__name__)


class CliMain(object):
    """
    Main class to manage CLI
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        self.server = None
        self.server_type = None
        self.username = None
        self.password = None
        self.i_username = None
        self.i_password = None
        self.credstore_file = None
        self.credstore_add = None
        self.configuration_file = None
        self.more = False
        self.session = None
        self.session_manager = None
        self.connector = None
        self.interactive = False
        self.current_dcli_command = None
        self.show_unreleased_apis = False
        self.metadata_manager = None
        self.default_options = None
        self.dcli_context = None
        self.cli_cmd_instance = None

    def init_main(self, interactive=False, **kwargs):
        """
        CliMain class init method

        :type  rpc: :class:`str`
        :param rpc: RPC protocol type
        :type  msg_protocol: :class:`str`
        :param msg_protocol: Message protocol type
        :type  server: :class:`str`
        :param server vAPI Server URL
        :type  username: :class:`str`
        :param username: Username
        :type  password: :class:`str`
        :param password: Password
        :type  skip_server_verification: :class:`bool`
        :param skip_server_verification: Skips server SSL verification process
        :type  cacert_file: :class:`str`
        :param cacert_file: CA certificate file
        :type  show_unreleased_apis: :class:`bool`
        :param show_unreleased_apis: Shows command and namespaces that are
               under development
        :type  more: :class:`str`
        :param more: More flag
        """
        self.server = kwargs.get('server')
        self.server_type = kwargs.get('server_type')
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.credstore_file = kwargs.get('credstore_file')
        self.credstore_add = kwargs.get('credstore_add')
        self.configuration_file = kwargs.get('configuration_file')
        self.more = kwargs.get('more')
        cacert_file = kwargs.get('cacert_file')
        skip_server_verification = kwargs.get('skip_server_verification')
        self.show_unreleased_apis = kwargs.get('show_unreleased_apis')
        self.session_manager = ''
        self.interactive = interactive

        context = self.get_dcli_context()
        try:
            self.default_options = Options(context)
        except ValueError:
            warning_msg = ("WARNING: Invalid configuration file detected: '%s'.\n"
                           "Turning off default options feature.") % (self.configuration_file)
            logger.warning(warning_msg)
            print(warning_msg)

        try:
            self.session = requests.Session()
            self.set_certificates_validation(cacert_file, skip_server_verification)

            if self.server_type in (ServerTypes.NSX,
                                    ServerTypes.VMC):
                self.connector = connect.get_requests_connector(self.session,
                                                                url=self.server,
                                                                msg_protocol='rest')
                credstore = CredStore()
                credstore.set_credstore_path(self.credstore_file)
                metadata_provider = \
                    LocalMetadataProvider(self.server_type,
                                          self.server,
                                          self.session,
                                          credstore)
            else:
                self.connector = connect.get_requests_connector(self.session,
                                                                url=self.server)
                metadata_provider = RemoteMetadataProvider(self.connector)
            self.metadata_manager = MetadataManager(metadata_provider)
        except Exception as e:
            error_msg = 'Unable to connect to the server.'
            msg = extract_error_msg(e)
            if msg:
                logger.error('Error: %s', msg)
            raise Exception(error_msg)

    def set_certificates_validation(self, cacert_file, skip_server_verification):
        """
        Sets certificates validation options to requests session according to
        users input

        :type  skip_server_verification: :class:`bool`
        :param skip_server_verification: Skips server SSL verification process
        :type  cacert_file: :class:`str`
        :param cacert_file: CA certificate file
        """
        if cacert_file:
            self.session.verify = cacert_file
        elif skip_server_verification:
            self.session.verify = False
        else:
            # if this is binary get trust store from binary's folder else get it from requests
            if getattr(sys, 'frozen', False):
                # The application is frozen
                certs_path = os.path.join(os.path.dirname(sys.executable),
                                          'cacert.pem')
            else:
                certs_path = requests.certs.where()
            certs_path = os.environ.get('DCLI_CACERTS_BUNDLE', certs_path)
            self.session.verify = certs_path

    def handle_user_and_password_input(self):
        """
        Method to prompt user to enter username, password and
        ask if they want to save credentials in credstore

        :rtype:  :class:`str`, :class:`str`
        :return: username, password
        """
        username, password, should_save = prompt_for_user_and_password(self.server_type)

        if not self.credstore_add:
            self.credstore_add = should_save

        return username, password

    def get_security_context(self, auth_scheme):
        """
        Method to get security context

        :rtype:  :class:`vmware.vapi.core.SecurityContext`
        :return: Security context
        """
        user = self.username
        pwd = self.password
        sec_ctx = None

        if pwd is False:
            # No credentials provided on command line; check credstore
            credstore = CredStore()
            credstore.set_credstore_path(self.credstore_file)
            logger.info('Trying to read credstore for login credentials')
            user, pwd = credstore.get_user_and_password(self.server,
                                                        self.session_manager,
                                                        user)

        if not user and self.interactive and self.i_username and self.i_password:
            user = self.i_username
            pwd = decrypt(self.i_password, self.server + user)

        if auth_scheme == USER_PASSWORD_SCHEME_ID:
            # In case user, pwd weren't provided then prompt for both
            if not user:
                self.username, self.password = self.handle_user_and_password_input()
                if self.interactive:
                    self.i_username = self.username
                    self.i_password = encrypt(self.password, self.server + self.username)
                return self.get_security_context(auth_scheme)
            else:
                self.username = user
                self.password = pwd

            if self.server_type == ServerTypes.VMC:
                token = get_vmc_authentication_token(self.session, pwd)
                sec_ctx = create_oauth_security_context(token)
            else:
                sec_ctx = create_user_password_security_context(user, pwd)
        elif auth_scheme == SAML_BEARER_SCHEME_ID:  # pylint: disable=too-many-nested-blocks
            token = os.environ.get('DCLI_SSO_BEARER_TOKEN', '')

            if not token:
                # Check if user passed STS URL environment variable
                sts_url = os.environ.get('STS_URL')
                try:
                    try:
                        from vmware.vapi.client.lib import sso
                    except ImportError:
                        handle_error('Unable to import SSO libraries')
                        sys.exit(StatusCode.INVALID_ENV)

                    auth = sso.SsoAuthenticator(sts_url)

                    # TODO: refactor this authentication code
                    if sts_url:
                        logger.info('Getting SAML bearer token')
                        if not user:
                            self.username, self.password = self.handle_user_and_password_input()
                            if self.interactive:
                                self.i_username = self.username
                                self.i_password = encrypt(self.password, self.server + self.username)

                        token = auth.get_bearer_saml_assertion(self.username,
                                                               self.password,
                                                               delegatable=True)
                    else:
                        # try passthrough authentication
                        logger.info('Using passthrough authentication')
                        token = auth.get_bearer_saml_assertion_gss_api(delegatable=True)
                except Exception as e:
                    msg = extract_error_msg(e)
                    handle_error('Unable to get SAML token for the user. %s' % msg)
                    return StatusCode.NOT_AUTHENTICATED
            sec_ctx = create_saml_bearer_security_context(token)

        return sec_ctx

    def authenticate_command(self, service, operation):  # pylint: disable=R0915
        """
        Method to authenticate vAPI command

        :type  service: :class:`str`
        :param service: vAPI service
        :type  operation: :class:`str`
        :param operation: vAPI operation

        :rtype:  :class:`StatusCode`
        :return: Return code of the authentication and whether it is session aware or sessionless
        """
        is_session_aware = False
        curr_auth_scheme = None
        authn_retval = StatusCode.SUCCESS
        auth_schemes = calculate_time(
            lambda: self.metadata_manager.get_authentication_schemes(
                service,
                operation),
            'get authentication schemes time')

        if not auth_schemes:
            return authn_retval, None

        sec_ctx = None
        # If authentication is required check if login credentials (username and password) were provided on the command line
        # If login credentials were provided by the user try to use them to execute the command
        # If login credentials were not provided check if the credstore has credentials for the server and session manager
        # If credstore has credentials for the provided server and session manager use them to execute the command
        # If no credentials were present in credstore try to execute the command using passthrough login

        # get curr auth scheme here and get session manager
        if USER_PASSWORD_SCHEME_ID in auth_schemes:
            logger.info('Using username/password authentication scheme')
            curr_auth_scheme = USER_PASSWORD_SCHEME_ID
        elif SAML_BEARER_SCHEME_ID in auth_schemes:
            logger.info('Using SAML bearer token authentication scheme')
            curr_auth_scheme = SAML_BEARER_SCHEME_ID
        elif NO_AUTHN_SCHEME in auth_schemes:
            logger.info('Using no authentication scheme')
            return StatusCode.SUCCESS, None
        else:
            handle_error('This command does not support login through username/password')
            return StatusCode.NOT_AUTHENTICATED, None

        # pick the first scheme be it session aware or session less
        is_session_aware = curr_auth_scheme and auth_schemes[curr_auth_scheme][0]

        if is_session_aware:
            self.session_manager = auth_schemes[curr_auth_scheme][0]

        user_pass_retry_count = 0
        # breaks when user/pass retry limit reached (for invalid creds) or at script block end(for valid creds)
        while True:
            sec_ctx = calculate_time(
                lambda: self.get_security_context(curr_auth_scheme),
                'get security context time')

            if sec_ctx == StatusCode.NOT_AUTHENTICATED:
                return sec_ctx, None

            user = self.username
            pwd = self.password
            self.username = None
            self.password = False

            if is_session_aware:
                self.connector.set_security_context(sec_ctx)
                logger.info('Doing session login to session manager')
                try:
                    authn_retval, result = calculate_time(
                        self.session_login,
                        'session login time')
                    if result and result.success():
                        session_id = result.output.value
                        # Execute subsequent calls using Session Identifier
                        sec_ctx = create_session_security_context(session_id)
                    else:
                        raise Exception('Unable to authenticate')
                except Exception:
                    self.i_username = None
                    self.i_password = None
                    if user_pass_retry_count < USER_PASS_RETRY_LIMIT:
                        user_pass_retry_count += 1
                        logger.info('Unsuccessful attempt for authentication. Try entering credentials again.')
                        print("Unable to authenticate user. Please enter the credentials again.")
                        continue
                    else:
                        error_str = 'Unable to authenticate user.'
                        if 'result' in locals() and result and result.error is not None:
                            handle_server_error(result.error)
                        else:
                            handle_error(error_str)
                        return StatusCode.NOT_AUTHENTICATED, None

            break

        self.connector.set_security_context(sec_ctx)

        if self.credstore_add:
            authn_retval = self.add_entry_to_credstore(user, pwd)

        return authn_retval, is_session_aware

    def add_entry_to_credstore(self, user, pwd):
        """
        Adds given credentials entry to the credstore.
        :param user: username
        :param pwd: password
        :return: Status code of the operation
        """
        logger.info("Adding credstore entry for user '%s'", user)
        credstore = CredStore()
        credstore.set_credstore_path(self.credstore_file)
        return credstore.add(self.server, user, pwd, self.session_manager)

    def session_login(self):
        """
        Method to login to SessionManager
        """
        return self.invoke_session_manager_method('create')

    def session_logout(self):
        """
        Method to logout from a SessionManager login session
        """
        self.invoke_session_manager_method('delete')
        self.session_manager = ''

    def invoke_session_manager_method(self, method_name):
        """
        Method to invoke session manger

        :type  method_name: :class:`str`
        :param method_name: Name of session manager method

        :rtype: :class:`StatusCode`
        :return: Error code
        :rtype: :class:`vmware.vapi.core.MethodResult`
        :return: Method result
        """
        if not self.session_manager:
            return StatusCode.NOT_AUTHENTICATED, None

        ctx = self.connector.new_context()
        sec_ctx = ctx.security_context
        ctx.security_context = None

        # Check if login method exists
        try:
            input_definition = calculate_time(
                lambda: self.metadata_manager.get_command_input_definition(
                    self.session_manager,
                    method_name),
                'get auth command input definition')
        except NotFound:
            # XXX remove this code once everyone moves over to create/delete methods
            if method_name == 'create':
                return self.invoke_session_manager_method('login')
            elif method_name == 'delete':
                return self.invoke_session_manager_method('logout')
            elif method_name == 'logout':
                logger.warning("No logout or delete method found")
                return StatusCode.NOT_AUTHENTICATED, None
            # no login method
            handle_error('Invalid login session manager found')
            return StatusCode.NOT_AUTHENTICATED, None

        api_provider = self.connector.get_api_provider()

        ctx.security_context = sec_ctx

        # Method call
        logger.debug('Invoking vAPI operation')
        result = api_provider.invoke(self.session_manager,
                                     method_name,
                                     input_definition.new_value(),
                                     ctx)
        return StatusCode.SUCCESS, result

    def get_cmd_instance(self, path, name):
        """
        Method to get CLICommand instance

        :type  path: :class:`str`
        :param path: CLI namespace path
        :type  name: :class:`str`
        :param name: CLI command name

        :rtype: :class:`CliCommand`
        :return: CliCommand instance
        """
        if self.cli_cmd_instance is None or \
                self.cli_cmd_instance.path != path or \
                self.cli_cmd_instance.name != name:
            self.cli_cmd_instance = CliCommand(self.server_type,
                                               self.connector,
                                               self.metadata_manager,
                                               self.default_options,
                                               path,
                                               name)
        return self.cli_cmd_instance

    def handle_command(self, cmd, args_, formatter, fp=sys.stdout, interactive_mode=False):
        """
        Main method to handle a vCLI command

        :type  cmd:  :class:`list` of :class:`str`
        :param cmd:  vCLI command
        :type  args_: :class:`list` of :class:`str`
        :param args_: Command arguments
        :type  formatter: :class:`str`
        :param formatter: Command formatter

        :rtype:  :class:`StatusCode`
        :return: Return code
        """
        op_id = str(uuid.uuid4())
        if self.show_unreleased_apis:
            app_ctx = ApplicationContext({OPID: op_id, SHOW_UNRELEASED_APIS: "True"})
        else:
            app_ctx = ApplicationContext({OPID: op_id})
        self.connector.set_application_context(app_ctx)

        path, name = CliHelper.get_command_path(cmd)

        try:
            cli_ns_instance = CliNamespace(self.metadata_manager, path, name)
        except Exception as e:
            msg = extract_error_msg(e)
            handle_error(msg, print_usage=True)
            return StatusCode.INVALID_ARGUMENT

        cli_cmd_instance = self.get_cmd_instance(path, name)
        if cli_ns_instance.is_a_namespace():
            cli_ns_instance.print_namespace_help(interactive_mode)
            return StatusCode.INVALID_COMMAND
        else:
            if cli_cmd_instance.is_a_command():
                retval, cmd_parser = cli_cmd_instance.get_command_parser()

                if retval != StatusCode.SUCCESS:
                    return retval

                # add command inputs to new argument parser
                cmd_input = None
                try:
                    cmd_input = cmd_parser.parse_args(args_)
                except ParsingError as e:
                    if cmd_input is not None and not cmd_input.help:
                        print(cmd_parser.print_help())
                    msg = extract_error_msg(e)
                    if msg:
                        handle_error('Failed while retrieving CLI command details: %s' % msg)
                    return StatusCode.INVALID_ARGUMENT
                except ParsingExit as e:
                    if cmd_input and not cmd_input.help:
                        print(cmd_parser.print_help())
                    msg = extract_error_msg(e)
                    if msg:
                        handle_error(msg)
                    return StatusCode.INVALID_ARGUMENT
                cli_cmd_instance.prompt_for_secret_fields(cmd_input)

                cmd_info = cli_cmd_instance.cmd_info

                user_pass_retry_count = 0
                # breaks when user/pass retry limit reached (for invalid creds) or at script block end(for valid creds)
                while True:
                    auth_result, is_session_aware = calculate_time(
                        lambda: self.authenticate_command(
                            cmd_info.service_id,
                            cmd_info.operation_id),
                        'full authentication time')
                    self.password = None
                    if auth_result != StatusCode.SUCCESS:
                        return auth_result
                    ctx = self.connector.new_context()
                    dcli_context = self.get_dcli_context()
                    result = calculate_time(lambda:
                                            cli_cmd_instance.execute_command(
                                                ctx,
                                                dcli_context,
                                                cmd_input,
                                                cmd_info.service_id,
                                                cmd_info.operation_id),
                                            'command call to the server time')

                    # Reset security context to None
                    self.connector.set_security_context(None)

                    formatter_instance = Formatter(cmd_info.formatter
                                                   if not formatter else formatter, fp)

                    if result.error:
                        if hasattr(result.error, 'name') and \
                                (result.error.name in (SERVER_UNAUTHENTICATED_ERROR,
                                                       SERVER_UNAUTHORIZED_ERROR)) and \
                                not is_session_aware and \
                                user_pass_retry_count < USER_PASS_RETRY_LIMIT and \
                                self.server_type not in (ServerTypes.NSX, ServerTypes.VMC):
                            user_pass_retry_count += 1
                        else:
                            break

                        logger.info('Unsuccessful attempt for authentication. Try entering credentials again.')
                        print("Unable to authenticate user. Please enter the credentials again.")
                        self.i_username = None
                        self.i_password = None
                        continue

                    break

                return calculate_time(lambda: cli_cmd_instance.display_result(result,
                                                                              formatter_instance,
                                                                              self.more),
                                      'display command output time')
            else:
                if not name and not path:
                    error_msg = 'Unable to execute command from the server.\n'
                    error_msg += 'Is server correctly configured?'
                    handle_error(error_msg)
                else:
                    command_name = name if not path else '%s %s' % (path.replace('.', ' '), name)
                    handle_error("Unknown command: '%s'" % command_name)
                return StatusCode.INVALID_COMMAND
            return StatusCode.INVALID_COMMAND

    def get_dcli_context(self):
        """
        Returns dcli context object
        @return: :class:`vmware.vapi.client.dcli.util.DcliContext`
        """
        if self.dcli_context is None:
            self.dcli_context = DcliContext(
                configuration_path=self.configuration_file,
                server=self.server,
                server_type=self.server_type)
        return self.dcli_context


def main(argv=None, fp=sys.stdout):
    """
    CLI client entry point
    """
    if argv is None:
        argv = sys.argv

    status = StatusCode.SUCCESS
    CliHelper.configure_logging('info')
    parser = CliHelper.get_parser(False)
    try:
        if six.PY2:
            input_ = [i.decode('utf-8') for i in argv[1:]]
        else:
            input_ = argv[1:]
        input_args = parser.parse_known_args(input_)

        try:
            is_interactive = input_args[0].interactive
        except Exception:
            is_interactive = False

        if input_args[0].loglevel != 'info':
            CliHelper.configure_logging(input_args[0].loglevel)

        cli_main = CliMain()
        if six.PY2:
            cli_main.current_dcli_command = ' '.join(item.decode('utf-8') for item in argv)
        else:
            cli_main.current_dcli_command = ' '.join(argv)
        shell = CliShell() if is_interactive and have_pyprompt else None
        credstore = CredStore()
        status = calculate_time(
            lambda: CliHelper.process_input(parser,
                                            input_args,
                                            cli_main,
                                            False,
                                            shell,
                                            credstore,
                                            fp),
            'dcli process execution time' if is_interactive else 'full command execution time',
            cli_main.current_dcli_command)
    except Exception as e:
        parser.print_usage()
        msg = extract_error_msg(e)
        handle_error(msg, print_usage=True)
        status = StatusCode.INVALID_COMMAND
    finally:
        save_report_to_file()

    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv))
