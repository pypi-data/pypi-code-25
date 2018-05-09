from __future__ import absolute_import
from __future__ import print_function

from xtt._ffi import ffi as _ffi
from xtt._ffi import lib as _lib
from xtt._ffi_utils import Buffer, BufferView, DataStruct

from xtt import Identity
from xtt.certificates import CertificateRootId
from xtt.crypto import ED25519PrivateKey, ED25519PublicKey, LRSWPseudonym
from xtt.exceptions import error_from_code, ReturnCode as RC

__all__ = [
    'ClientHandshakeContext', 'ClientLRSWGroupContext',
]

class ClientLRSWGroupContext(object):
    """
    Holds the DAA group credentials and configuration for the client.
    """

    def __init__(self, group_id, priv_key, credential, basename):
        self.native = _ffi.new('struct xtt_client_group_context*')

        if self.native == _ffi.NULL:
            raise MemoryError("Unable to allocate native object")

        rc = _lib.xtt_initialize_client_group_context_lrsw(self.native,
                                                           group_id.native,
                                                           priv_key.native,
                                                           credential.native,
                                                           basename,
                                                           len(basename))
        if rc != RC.SUCCESS:
            raise MemoryError("Unable to allocate native object")

class ClientHandshakeContext(object):
    """
    The ClientHandshakeContext holds the configuration options and
    data needed by a client while performing an XTT identity handshake.
    """

    def __init__(self, version, suite_spec):
        self.native = _ffi.new('struct xtt_client_handshake_context*')

        if self.native == _ffi.NULL:
            raise MemoryError("Unable to allocate native object")

        self._in  = Buffer(_lib.max_handshake_server_message_length())
        self._out = Buffer(_lib.max_handshake_client_message_length())
        self._io = BufferView()

        self._version = version
        self._suite_spec = suite_spec

        self._server_root_id = CertificateRootId()

        rc = _lib.xtt_initialize_client_handshake_context(self.native,
                                                          self._in.native,
                                                          self._in.size,
                                                          self._out.native,
                                                          self._out.size,
                                                          version,
                                                          suite_spec)

        if rc != RC.SUCCESS:
            raise error_from_code(rc)

    @property
    def io_buffer(self):
        return self._io.buffer

    @property
    def version(self):
        return self._version

    @property
    def suite_spec(self):
        return self._suite_spec

    @property
    def server_root_id(self):
        return self._server_root_id

    @property
    def my_longterm_public_key_ed25519(self):
        pub = ED25519PublicKey()
        rc = _lib.xtt_get_my_longterm_key_ed25519(pub.native, self.native)
        if rc == RC.SUCCESS:
            return pub
        else:
            raise error_from_code(rc)

    @property
    def my_longterm_private_key_ed25519(self):
        priv = ED25519PrivateKey()
        rc = _lib.xtt_get_my_longterm_private_key_ed25519(priv.native, self.native)
        if rc == RC.SUCCESS:
            return priv
        else:
            raise error_from_code(rc)

    @property
    def my_identity(self):
        ident = Identity()
        rc = _lib.xtt_get_my_identity(ident.native, self.native)
        if rc == RC.SUCCESS:
            return ident
        else:
            raise error_from_code(rc)

    @property
    def my_pseudonym_lrsw(self):
        pseudonym = LRSWPseudonym()
        rc = _lib.xtt_get_my_pseudonym_lrsw(pseudonym.native)
        if rc == RC.SUCCESS:
            return pseudonym
        else:
            raise error_from_code(rc)

    def handle_io(self, bytes_sent, bytes_recv):
        rc = _lib.xtt_handshake_client_handle_io(bytes_sent, bytes_recv,
                                                 self._io.addressof_size,
                                                 self._io.addressof_data,
                                                 self.native)
        if rc != RC.SUCCESS and rc != RC.HANDSHAKE_FINISHED:
            raise error_from_code(rc)

    def start(self):
        rc = _lib.xtt_handshake_client_start(self._io.addressof_size,
                                             self._io.addressof_data,
                                             self.native)
        if rc != RC.SUCCESS and rc != RC.HANDSHAKE_FINISHED:
            raise error_from_code(rc)

    def preparse_server_attest(self, server_root_id):
        rc = _lib.xtt_handshake_client_preparse_serverattest(self._server_root_id.native,
                                                             self._io.addressof_size,
                                                             self._io.addressof_data,
                                                             self.native)
        if rc != RC.SUCCESS and rc != RC.HANDSHAKE_FINISHED:
            raise error_from_code(rc)

    def build_id_client_attest(self, root_cert, server_id, identity, group_context):
        rc = _lib.xtt_handshake_client_build_idclientattest(self._io.addressof_size,
                                                            self._io.addressof_data,
                                                            root_cert.native,
                                                            identity.native,
                                                            server_id.native,
                                                            group_context.native,
                                                            self.native)
        if rc != RC.SUCCESS and rc != RC.HANDSHAKE_FINISHED:
            raise error_from_code(rc)

    def parse_id_server_finished(self):
        rc = _lib.xtt_handshake_client_parse_idserverfinished(self._io.addressof_size,
                                                              self._io.addressof_data,
                                                              self.native)
        if rc != RC.SUCCESS and rc != RC.HANDSHAKE_FINISHED:
            raise error_from_code(rc)
