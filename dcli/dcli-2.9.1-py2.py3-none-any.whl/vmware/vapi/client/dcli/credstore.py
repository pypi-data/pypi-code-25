"""
This module handles dcli credstore operations
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright (c) 2015-2018 VMware, Inc.  All rights reserved. '
__license__ = 'SPDX-License-Identifier: MIT'
__docformat__ = 'epytext en'

import os
import stat
import logging
import six
from vmware.vapi.client.dcli.util import (
    StatusCode, encrypt, decrypt)
from vmware.vapi.client.dcli.exceptions import extract_error_msg, handle_error
try:
    import simplejson as json
except ImportError:
    import json

logger = logging.getLogger(__name__)


try:
    from ctypes import windll, create_string_buffer
    import msvcrt

    # XXX: Pepify all the names
    class AutoFileLockBase(object):
        """
        Base class for windows credstore file locking
        """
        # Size of 64 bits OVERLAPPED struct
        _OVERLAPPED_BUFSIZE = 8 * 2 + 4 * 2 + 8

        # Lock region low, high dword
        _LOCK_LOW, _LOCK_HIGH = 0x0, 0x80000000

        def __init__(self):
            pass

        @staticmethod
        def _GetLockFlags():
            """
            Returns flag for SHARED, EXCLUSIVE, FLAGS_NB
            """
            return 0x0, 0x2, 0x1

        @staticmethod
        def _GetHandle(fd):
            """
            Get Windows Handle from python file handle
            """
            return msvcrt.get_osfhandle(fd.fileno())

        @staticmethod
        def _LockFile(fd, op):
            """
            Lock file
            """
            hdl = AutoFileLockBase._GetHandle(fd)
            dwReserved = 0
            overlapped = create_string_buffer(AutoFileLockBase._OVERLAPPED_BUFSIZE)
            ret = windll.kernel32.LockFileEx(hdl, op, dwReserved,
                                             AutoFileLockBase._LOCK_LOW,
                                             AutoFileLockBase._LOCK_HIGH,
                                             overlapped)
            if ret == 0:
                dwError = windll.kernel32.GetLastError()
                ioError = IOError("%d" % dwError)
                if dwError == 33:  # ERROR_LOCK_VIOLATION
                    import errno
                    ioError.errno = errno.EAGAIN
                raise ioError

        @staticmethod
        def _UnlockFile(fd):
            """
            Unlock file
            """
            hdl = AutoFileLockBase._GetHandle(fd)
            dwReserved = 0
            overlapped = create_string_buffer(AutoFileLockBase._OVERLAPPED_BUFSIZE)
            windll.kernel32.UnlockFileEx(hdl, dwReserved,
                                         AutoFileLockBase._LOCK_LOW,
                                         AutoFileLockBase._LOCK_HIGH,
                                         overlapped)
except ImportError:
    import fcntl

    class AutoFileLockBase(object):
        """
        Base class for posix credstore file locking
        """
        def __init__(self):
            pass

        @staticmethod
        def _GetLockFlags():
            """
            Returns flag for SHARED, EXCLUSIVE, FLAGS_NB
            """
            return fcntl.LOCK_SH, fcntl.LOCK_EX, fcntl.LOCK_NB

        @staticmethod
        def _LockFile(fd, op):
            """
            Lock file
            """
            # Note:
            # - If IOError with [Errno 9] Bad file descriptor, check to make
            #   sure fd is opened with "r+" / "w+"
            # - If non-blocking, but will block, lockf will raise IOError, with
            #   errno set to EACCES or EAGAIN
            fcntl.lockf(fd, op)

        @staticmethod
        def _UnlockFile(fd):
            """
            Unlock file
            """
            fcntl.lockf(fd, fcntl.LOCK_UN)


class AutoFileLock(AutoFileLockBase):
    """
    Class to provide platform independent locking for an open file
    """
    SHARED, EXCLUSIVE, FLAGS_NB = AutoFileLockBase._GetLockFlags()

    # AutoFileLock init
    # @param fd Open file handle
    # @param op SHARED / EXCLUSIVE, optionally or with FLAGS_NB for
    #           non-blocking
    #           If non-blocking and will block, __init__ will raise IOError,
    #           with errno set to EACCES or EAGAIN
    def __init__(self, fd, op):
        """
        AutoFileLock init

        :type  fd: File handle
        :param fd: Open file handle
        :type  op: Locking flags
        :param op: SHARED / EXCLUSIVE, optionally or with FLAGS_NB for
                   non-blocking.
                   If non-blocking and will block, __init__ will raise IOError,
                   with errno set to EACCES or EAGAIN
        """
        super(AutoFileLock, self).__init__()
        self.fd = None
        self._LockFile(fd, op)
        self.fd = fd

    def __enter__(self):
        return self.fd

    def __exit__(self, exc_type, exc_value, traceback):
        if self.fd:
            self._UnlockFile(self.fd)
            self.fd = None


class CredStore(object):
    """
    Class to provide credential store operations for dcli
    """

    _CREDSTORE = 'credstore'
    _SERVER = 'server'
    _USER = 'user'
    _PASSWORD = 'password'
    _SESSION_MGR = 'session_manager'

    def __init__(self):
        """
        CredStore init method
        """
        self.credstore_path = None

    def set_credstore_path(self, credstore_path):
        """
        Set CredStore Path

        :type   credstore_path: :class:`str`
        :param  credstore_path: Path to credential store file
        """
        self.credstore_path = credstore_path.encode('utf-8')

    def add(self, server, user, pwd, session_mgr):
        """
        Add a credential store entry to credstore file

        :type   server: :class:`str`
        :param  server: vAPI server URL
        :type   user: :class:`str`
        :param  user: User name to be stored
        :type   pwd: :class:`str`
        :param  pwd: Plain-text password to be stored
        :type   session_mgr: :class:`str`
        :param  session_mgr: Session manager

        :rtype:  :class:`StatusCode`
        :return: Status code
        """
        encrypted_pwd = encrypt(pwd, server + user + session_mgr)
        if six.PY3:
            encrypted_pwd = encrypted_pwd.decode()
        del pwd

        found = False
        try:
            umask_original = os.umask(0)
            # Only owner should have read-write permissions
            mode = stat.S_IRUSR | stat.S_IWUSR  # This is 0o600 in octal

            # Open and share lock credstore file
            with os.fdopen(os.open(self.credstore_path, os.O_RDWR | os.O_CREAT, mode), 'r+') as fd:
                with AutoFileLock(fd, AutoFileLock.SHARED) as locked_fd:
                    credstore = {}
                    entries = []
                    try:
                        credstore = json.load(locked_fd)
                    except ValueError:
                        # Likely empty credstore file, ignore error and move on
                        pass

                    if credstore:
                        entries = credstore.get(self._CREDSTORE)
                        for entry in entries:
                            json_server = entry.get(self._SERVER)
                            json_session_mgr = entry.get(self._SESSION_MGR)
                            json_user = entry.get(self._USER)

                            if json_server == server and json_user == user and json_session_mgr == session_mgr:
                                # update the password
                                entry[self._PASSWORD] = encrypted_pwd
                                found = True
                                break

                    if not found:
                        # create new credstore entry
                        new_entry = {}
                        new_entry[self._SERVER] = server
                        new_entry[self._SESSION_MGR] = session_mgr
                        new_entry[self._USER] = user
                        new_entry[self._PASSWORD] = encrypted_pwd
                        entries.append(new_entry)

                    credstore[self._CREDSTORE] = entries
                    locked_fd.seek(0)
                    locked_fd.truncate()
                    locked_fd.write(json.dumps(credstore, indent=4) + '\n')
                    return StatusCode.SUCCESS
        except IOError as e:
            msg = extract_error_msg(e)
            if msg:
                error_msg = 'Unable to open credstore file %s.'\
                            'Message: %s' % (self.credstore_path, msg)
                handle_error(error_msg)
            return StatusCode.INVALID_ENV
        finally:
            os.umask(umask_original)

    def remove(self, server, user, session_mgr):
        """
        Remove a credential store entry from credstore file

        :type   server: :class:`str`
        :param  server: vAPI server URL
        :type   user: :class:`str`
        :param  user: User name
        :type   session_mgr: :class:`str`
        :param  session_mgr: Session manager, if session manager is None and if only 1 entry exists
                for given user and server it will be removed

        :rtype:  :class:`StatusCode`
        :return: Status code
        """
        try:
            # Open and share lock credstore file
            with open(self.credstore_path, 'r+') as fd:
                with AutoFileLock(fd, AutoFileLock.SHARED) as locked_fd:
                    credstore = {}
                    try:
                        credstore = json.load(locked_fd)
                    except ValueError:
                        error_msg = 'Invalid credstore file %s' % self.credstore_path
                        handle_error(error_msg)
                        return StatusCode.INVALID_ENV

                    entries = credstore.get(self._CREDSTORE)

                    # remove node with given server/user/session_mgr combination
                    try:
                        if session_mgr:
                            new_entries = [entry for entry in entries
                                           if not (entry.get(self._SERVER) == server and
                                                   entry.get(self._SESSION_MGR) == session_mgr and
                                                   entry.get(self._USER) == user)]
                            if new_entries == entries:
                                raise Exception()
                        else:
                            entry_match = []
                            new_entries = []
                            for entry in entries:
                                if entry.get(self._SERVER) == server:
                                    if not user or entry.get(self._USER) == user:
                                        entry_match.append(entry)
                                else:
                                    new_entries.append(entry)

                            if not entry_match:
                                raise Exception()

                            if len(entry_match) > 1:
                                handle_error('Found more than one credstore entry for given user and server, pass session manager')
                                return StatusCode.INVALID_COMMAND
                    except Exception as e:
                        err_msg = "Couldn't find credstore entry. "
                        err_msg += "Please pass correct user and server values"
                        handle_error(err_msg)
                        return StatusCode.INVALID_COMMAND
                    credstore[self._CREDSTORE] = new_entries
                    locked_fd.seek(0)
                    locked_fd.truncate()
                    locked_fd.write(json.dumps(credstore, indent=4) + '\n')
                    return StatusCode.SUCCESS
        except IOError as e:
            msg = extract_error_msg(e)
            if msg:
                error_msg = 'Unable to open credstore file %s.'\
                            'Message: %s' % (self.credstore_path, msg)
                handle_error(error_msg)
            return StatusCode.INVALID_ENV

    def list(self, formatter='table'):
        """
        List credential store entries from credstore file

        :type   formatter: :class:`str`
        :param  formatter: Output formatter

        :rtype:  :class:`StatusCode`
        :return: Status code
        """
        credstore = {}
        # Open and share lock credstore file
        try:
            with open(self.credstore_path, 'r+') as fd:
                with AutoFileLock(fd, AutoFileLock.SHARED) as locked_fd:
                    try:
                        credstore = json.load(locked_fd)
                    except ValueError:
                        error_msg = 'Invalid credstore file %s' % self.credstore_path
                        handle_error(error_msg)
                        return StatusCode.INVALID_ENV
        except IOError as e:
            msg = extract_error_msg(e)
            if msg:
                error_msg = 'Unable to open credstore file %s.'\
                            'Message: %s' % (self.credstore_path, msg)
                handle_error(error_msg)
            return StatusCode.INVALID_ENV

        from vmware.vapi.data.value import (StringValue, StructValue, ListValue)

        entries = credstore.get(self._CREDSTORE)
        list_val = ListValue()
        for entry in entries:
            json_server = entry.get(self._SERVER)
            json_session_mgr = entry.get(self._SESSION_MGR)
            json_user = entry.get(self._USER)

            # create a struct value of server/user and session mgr values
            struct_val = StructValue('credstore')
            struct_val.set_field('server', StringValue(json_server))
            struct_val.set_field('session_manager', StringValue(json_session_mgr))
            struct_val.set_field('user', StringValue(json_user))
            list_val.add(struct_val)

        from vmware.vapi.client.lib.formatter import Formatter
        formatter_inst = Formatter(formatter)
        formatter_inst.format_output(list_val)
        return StatusCode.SUCCESS

    def get_user_and_password(self, server, session_mgr, user):
        """
        Get username and password tuple for a specific user/server/session manager
        entry in credstore file

        :type   server: :class:`str`
        :param  server: vAPI server URL
        :type   session_mgr: :class:`str`
        :param  session_mgr: Session manager
        :type   user: :class:`str`
        :param  user: User name

        :rtype:  :class:`str`
        :return: Username
        :rtype:  :class:`str`
        :return: Password
        """
        credstore = {}
        try:
            # Open and share lock credstore file
            with open(self.credstore_path, 'r+') as fd:
                with AutoFileLock(fd, AutoFileLock.SHARED) as locked_fd:
                    try:
                        # open json file in read mode and create a struct value of server/user and session mgr values
                        credstore = json.load(locked_fd)
                    except ValueError:
                        return user, None
        except IOError:
            return user, None

        entries = credstore.get(self._CREDSTORE)
        password_tuple = [(entry.get(self._USER), entry.get(self._PASSWORD)) for entry in entries
                          if entry.get(self._SERVER) == server and entry.get(self._SESSION_MGR) == session_mgr]

        password = None
        username = None
        if user:
            password_list = [pwd for username, pwd in password_tuple if username == user]
            if password_list:
                username = user
                password = decrypt(password_list[0], server + user + session_mgr)
        else:
            if len(password_tuple) == 1:  # If there's only one user return the password
                username = password_tuple[0][0]
                password = decrypt(password_tuple[0][1], server + password_tuple[0][0] + session_mgr)
        return username, password
