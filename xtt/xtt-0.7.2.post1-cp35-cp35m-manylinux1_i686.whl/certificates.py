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

from datetime import datetime

from xtt._ffi import ffi as _ffi
from xtt._ffi import lib as _lib
from xtt._ffi_utils import DataStruct
from xtt._utils import _check_len, to_bytes, to_text

from xtt import Identity, SignatureType
from xtt.crypto import ED25519PublicKey
from xtt.exceptions import error_from_code, ReturnCode as RC

__all__ = [
    'generate_ed25519_server_certificate',
    'CertificateExpiry', 'CertificateRootId', 'ED25519ServerCertificate',
    'ED25519RootCertificateContext'
]

def generate_ed25519_server_certificate(server_id, server_pub_key, expiry,
                                        root_id, root_priv_key):
    """
    Creates a new server certificate signed by the provided root.

    :param Identity server_id: the identity for the certificate
    :param ED25519PublicKey server_pub_key: the public key for the certificate
    :param CertificateExpiry expiry: the expiry date for the certificate
    :param CertificateRootId root_id: the root identity to sign this certificate
    :param ED25519PrivateKey root_priv_key: the root private key to sign this
                                            certificate
    """
    cert = ED25519ServerCertificate()
    rc = _lib.xtt_generate_server_certificate_ed25519(cert.native,
                                                      server_id.native,
                                                      server_pub_key.native,
                                                      expiry.native,
                                                      root_id.native,
                                                      root_priv_key.native)
    if rc == RC.SUCCESS:
        return cert
    else:
        raise error_from_code(rc)

class CertificateExpiry(DataStruct):
    """
    The expiry date of a certificate, specified as YYYYMMDD.
    """
    struct = "xtt_certificate_expiry"

    _format = '%Y%m%d'

    @classmethod
    def from_datetime(cls, date):
        raw = date.strftime(cls._format)
        return cls(to_bytes(raw))

    @property
    def datetime(self):
        return datetime.strptime(to_text(self.data), self._format)

    def __str__(self):
        return str(self.datetime)

class CertificateRootId(DataStruct):
    """
    The identity of a root certificate.
    """
    struct = "xtt_certificate_root_id"

class ServerCertificate(object):
    """
    A certificate for an XTT server that is used to let the client
    authenticate the server.
    """

    @classmethod
    def from_file(cls, filename):
        with open(filename, 'rb') as f:
            raw = f.read()
            return cls(raw)

    def __init__(self, size, value=None):
        self.native = _ffi.new('unsigned char[]', size)

        if self.native == _ffi.NULL:
            raise MemoryError("Unable to allocate native object")

        self._raw = _ffi.cast('struct xtt_server_certificate_raw_type*',
                              self.native)

        if value:
            self.data = value

    def __str__(self):
        return "%s(id: %s, public_key: %s..., expiry: %s, root_id: %s)"%(type(self).__name__,
                                                                         str(self.id),
                                                                         str(self.public_key)[-10:],
                                                                         str(self.expiry),
                                                                         str(self.root_id))

    def __repr__(self):
        return "%s(%s)"%(type(self).__name__, repr(self.data))

    @property
    def data(self):
        return _ffi.buffer(self.native)[:]

    @data.setter
    def data(self, value):
        _check_len(self.native, value)
        _ffi.memmove(self.native, value, len(value))

    @property
    def id(self):
        value = _lib.xtt_server_certificate_access_id(self._raw)
        buff = _ffi.buffer(value, Identity.sizeof)
        return Identity(buff)

    @property
    def expiry(self):
        value = _lib.xtt_server_certificate_access_expiry(self._raw)
        buff = _ffi.buffer(value, CertificateExpiry.sizeof)
        return CertificateExpiry(buff)

    @property
    def root_id(self):
        value = _lib.xtt_server_certificate_access_rootid(self._raw)
        buff = _ffi.buffer(value, CertificateRootId.sizeof)
        return CertificateRootId(buff)

class ED25519ServerCertificate(ServerCertificate):
    """
    A :ServerCertificate: using ED25519 keys.
    """

    def __init__(self, value=None):
        size = _lib.xtt_server_certificate_length_fromsignaturetype(SignatureType.ED25519)
        super(ED25519ServerCertificate, self).__init__(size, value)

    @property
    def public_key(self):
        value = _lib.xtt_server_certificate_access_pubkey(self._raw)
        buff = _ffi.buffer(value, ED25519PublicKey.sizeof)
        return ED25519PublicKey(buff)

class ED25519RootCertificateContext(object):
    """A root certificate id and public key
    """

    def __init__(self, root_id, root_pubkey):
        self.native = _ffi.new('struct xtt_server_root_certificate_context*')

        if self.native == _ffi.NULL:
            raise MemoryError("Unable to allocate native object")

        rc = _lib.xtt_initialize_server_root_certificate_context_ed25519(self.native,
                                                                         root_id.native,
                                                                         root_pubkey.native)
        if rc != RC.SUCCESS:
            error_from_code(rc)
