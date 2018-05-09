# Copyright 2018 Xaptum, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License

from __future__ import absolute_import
from __future__ import print_function

from xtt._ffi import ffi as _ffi
from xtt._ffi import lib as _lib
from xtt._ffi_utils import Buffer, BufferView, DataStruct

from xtt import GroupId, Identity
from xtt.crypto import ED25519PublicKey, LRSWPseudonym
from xtt.exceptions import error_from_code, ReturnCode as RC

__all__ = [
    'LRSWGroupPublicKeyContext', 'ServerCookieContext',
    'ServerED25519CertificateContext', 'ServerHandshakeContext'
]

class LRSWGroupPublicKeyContext(object):
    """
    Holds a DAA group public key and configuration.
    """

    def __init__(self, pub_key, basename):
        self.native = _ffi.new('struct xtt_group_public_key_context*')

        if self.native == _ffi.NULL:
            raise MemoryError("Unable to allocate native object")

        rc = _lib.xtt_initialize_group_public_key_context_lrsw(self.native,
                                                               basename,
                                                               len(basename),
                                                               pub_key.native)
        if rc != RC.SUCCESS:
            raise MemoryError("Unable to allocate native object")

class ServerCookieContext(object):
    """
    """

    def __init__(self):
        self.native = _ffi.new('struct xtt_server_cookie_context*')

        if self.native == _ffi.NULL:
            raise MemoryError("Unable to allocate native object")

        rc = _lib.xtt_initialize_server_cookie_context(self.native)
        if rc != RC.SUCCESS:
            raise error_from_code(rc)

class ServerED25519CertificateContext(object):
    """
    Holds the certificate and signing key used to authenticate the
    server to the client.
    """

    def __init__(self, cert, key):
        self.native = _ffi.new('struct xtt_server_certificate_context*')

        if self.native == _ffi.NULL:
            raise MemoryError("Unable to allocate native object")

        rc = _lib.xtt_initialize_server_certificate_context_ed25519(self.native,
                                                                    cert.native,
                                                                    key.native)
        if rc != RC.SUCCESS:
            error_from_code(rc)

class ServerHandshakeContext(object):
    """
    The ServerHandshakeContext holds the configuration options and
    data needed by the server while performing an XTT identity handshake.
    """

    def __init__(self):
        self.native = _ffi.new('struct xtt_server_handshake_context*')

        if self.native == _ffi.NULL:
            raise MemoryError("Unable to allocate native object")

        self._in  = Buffer(_lib.max_handshake_client_message_length())
        self._out = Buffer(_lib.max_handshake_server_message_length())
        self._io = BufferView()

        self._client_requested_id  = Identity()
        self._client_claimed_group = GroupId()

        rc = _lib.xtt_initialize_server_handshake_context(self.native,
                                                          self._in.native,
                                                          self._in.size,
                                                          self._out.native,
                                                          self._out.size)

        if rc != RC.SUCCESS:
            raise error_from_code(rc)

    @property
    def io_buffer(self):
        return self._io.buffer

    @property
    def version(self):
        version = _ffi.new('xtt_version*')
        rc = _lib.xtt_get_version(version, self.native)
        if rc == RC.SUCCESS:
            return version[0]
        else:
            raise error_from_code(rc)

    @property
    def suite_spec(self):
        spec = _ffi.new('suite_spec*')
        rc = _lib.xtt_get_suite_spec(spec, self.native)
        if rc == RC.SUCCESS:
            return spec[0]
        else:
            raise error_from_code(rc)

    @property
    def client_requested_identity(self):
        return self._client_requested_id

    @property
    def client_claimed_group(self):
        return self._client_claimed_group

    @property
    def client_longterm_key_ed25519(self):
        pub = ED25519PublicKey()
        rc = _lib.xtt_get_clients_longterm_key_ed25519(pub.native, self.native)
        if rc == RC.SUCCESS:
            return pub
        else:
            raise error_from_code(rc)

    @property
    def client_identity(self):
        id = Identity()
        rc = _lib.xtt_get_clients_identity(id.native, self.native)
        if rc == RC.SUCCESS:
            return id
        else:
            raise error_from_code(rc)

    @property
    def client_pseudonym_lrsw(self):
        pseudonym = LRSWPseudonym()
        rc = _lib.xtt_get_clients_pseudonym_lrsw(pseudonym.native, self.native)
        if rc == RC.SUCCESS:
            return pseudonym
        else:
            raise error_from_code(rc)

    def handle_io(self, bytes_sent, bytes_recv):
        rc = _lib.xtt_handshake_server_handle_io(bytes_sent, bytes_recv,
                                                 self._io.addressof_size,
                                                 self._io.addressof_data,
                                                 self.native)
        if rc != RC.SUCCESS and rc != RC.HANDSHAKE_FINISHED:
            raise error_from_code(rc)

    def handle_connect(self):
        rc = _lib.xtt_handshake_server_handle_connect(self._io.addressof_size,
                                                      self._io.addressof_data,
                                                      self.native)
        if rc != RC.SUCCESS and rc != RC.HANDSHAKE_FINISHED:
            raise error_from_code(rc)

    def build_server_attest(self, server_cert_ctx, server_cookie_ctx):
        rc = _lib.xtt_handshake_server_build_serverattest(self._io.addressof_size,
                                                          self._io.addressof_data,
                                                          self.native,
                                                          server_cert_ctx.native,
                                                          server_cookie_ctx.native)
        if rc != RC.SUCCESS and rc != RC.HANDSHAKE_FINISHED:
            raise error_from_code(rc)

    def preparse_id_client_attest(self, server_cert_ctx, server_cookie_ctx):
        rc = _lib.xtt_handshake_server_preparse_idclientattest(self._io.addressof_size,
                                                               self._io.addressof_data,
                                                               self._client_requested_id.native,
                                                               self._client_claimed_group.native,
                                                               server_cookie_ctx.native,
                                                               server_cert_ctx.native,
                                                               self.native)
        if rc != RC.SUCCESS and rc != RC.HANDSHAKE_FINISHED:
            raise error_from_code(rc)

    def verify_group_signature(self, gpk_ctx, server_cert_ctx):
        rc = _lib.xtt_handshake_server_verify_groupsignature(self._io.addressof_size,
                                                             self._io.addressof_data,
                                                             gpk_ctx.native,
                                                             server_cert_ctx.native,
                                                             self.native)
        if rc != RC.SUCCESS and rc != RC.HANDSHAKE_FINISHED:
            raise error_from_code(rc)

    def build_id_server_finished(self, client_id):
        rc = _lib.xtt_handshake_server_build_idserverfinished(self._io.addressof_size,
                                                              self._io.addressof_data,
                                                              client_id.native,
                                                              self.native)
        if rc != RC.SUCCESS and rc != RC.HANDSHAKE_FINISHED:
            raise error_from_code(rc)
