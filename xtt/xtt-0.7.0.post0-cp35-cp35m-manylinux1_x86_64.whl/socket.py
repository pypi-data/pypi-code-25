from __future__ import absolute_import
from __future__ import print_function

from xtt.exceptions import *

from xtt import Identity
from xtt.certificates import ED25519RootCertificateContext, CertificateRootId
from xtt.server import ServerCookieContext, ServerHandshakeContext
from xtt.client import ClientHandshakeContext

__all__ = ['XTTClientSocket', 'XTTServerSocket']

class XTTClientSocket(object):

    def __init__(self, sock, version, suite_spec, group_context, server_id,
                 root_id, root_pubkey, identity=None):
        self._sock = sock
        self._server_root_id = CertificateRootId()
        self._root_cert = ED25519RootCertificateContext(root_id, root_pubkey)
        self._server_id = server_id
        self._identity  = identity or Identity()
        self._group_ctx = group_context
        self._ctx = ClientHandshakeContext(version, suite_spec)

    @property
    def identity(self):
        return self._ctx.my_identity

    def _do(self, step, *args):
        try:
            step(*args)
        except XTTWantReadError:
            self.do_read()
        except XTTWantWriteError:
            self.do_write()
        except XTTWantPreparseServerAttestError:
            self.do_preparse_server_attest()
        except XTTWantBuildIdClientAttestError:
            self.do_build_id_client_attest()
        except XTTWantParseIdServerFinishedError:
            self.do_parse_id_server_finished()

    def start(self):
        self._do(self._ctx.start)

    def do_read(self):
        buf = self._ctx.io_buffer
        cnt = self._sock.recv_into(buf, len(buf))
        self._do(self._ctx.handle_io, 0, cnt)

    def do_write(self):
        buf = self._ctx.io_buffer
        cnt = self._sock.send(buf)
        self._do(self._ctx.handle_io, cnt, 0)

    def do_preparse_server_attest(self):
        self._do(self._ctx.preparse_server_attest, self._server_root_id)

    def do_build_id_client_attest(self):
        self._do(self._ctx.build_id_client_attest,
                 self._root_cert,
                 self._server_id,
                 self._identity,
                 self._group_ctx)

    def do_parse_id_server_finished(self):
        self._do(self._ctx.parse_id_server_finished)

class XTTServerSocket(object):

    def __init__(self, sock, cert_context, group_from_id, assign_client_id):
        self._sock = sock
        self._cert_ctx = cert_context
        self._cookie_ctx = ServerCookieContext()
        self._group_from_id = group_from_id
        self._assign_client_id = assign_client_id
        self._ctx = ServerHandshakeContext()

    def _do(self, step, *args):
        try:
            step(*args)
        except XTTWantReadError:
            self.do_read()
        except XTTWantWriteError:
            self.do_write()
        except XTTWantBuildServerAttestError:
            self.do_build_server_attest()
        except XTTWantPreparseIdClientAttestError:
            self.do_preparse_id_client_attest()
        except XTTWantVerifyGroupSignatureError:
            self.do_verify_group_signature()
        except XTTWantBuildIdServerFinishedError:
            self.do_build_id_server_finished()

    def handle_connect(self):
        self._do(self._ctx.handle_connect)

    def do_read(self):
        buf = self._ctx.io_buffer
        cnt = self._sock.recv_into(buf, len(buf))
        self._do(self._ctx.handle_io, 0, cnt)

    def do_write(self):
        buf = self._ctx.io_buffer
        cnt = self._sock.send(buf)
        self._do(self._ctx.handle_io, cnt, 0)

    def do_build_server_attest(self):
        self._do(self._ctx.build_server_attest, self._cert_ctx, self._cookie_ctx)

    def do_preparse_id_client_attest(self):
        self._do(self._ctx.preparse_id_client_attest, self._cert_ctx, self._cookie_ctx)

    def do_verify_group_signature(self):
        group = self._group_from_id(self._ctx.client_claimed_group)
        if not group:
            raise ValueError("Invalid Group")
        self._do(self._ctx.verify_group_signature, group, self._cert_ctx)

    def do_build_id_server_finished(self):
        assigned_id = self._assign_client_id(self._ctx.client_requested_identity,
                                             self._ctx.client_claimed_group,
                                             self._ctx.client_pseudonym_lrsw)
        if not assigned_id:
            raise ValueError("Invalid Identity")
        self._do(self._ctx.build_id_server_finished, assigned_id)
