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

from xtt.exceptions import error_from_code, ReturnCode as RC

__all__ = [
    'x509_from_ed25519_key_pair', 'asn1_from_ed25519_private_key'
]

def x509_from_ed25519_key_pair(pub_key, priv_key, common_name):
    """
    Creates a self-signed x509 certificate for a common name and
    ED25519 key pair.

    :pub_key: an ED25519PublicKey instance
    :priv_key: an ED25519PrivateKey instance
    :common_name: an XTTIdentity instance
    :returns: the certificate as a byte string
    """
    cert_len = _lib.xtt_x509_certificate_length()
    cert = _ffi.new('unsigned char[]', cert_len)
    rc = _lib.xtt_x509_from_ed25519_keypair(pub_key.native,
                                           priv_key.native,
                                           common_name.native,
                                           cert, len(cert))
    if rc == RC.SUCCESS:
        return _ffi.buffer(cert)[:]
    else:
        raise error_from_code(rc)

def asn1_from_ed25519_private_key(priv_key):
    """
    Returns the ASN.1 encoding of a ED25519 private ket.

    :priv_key: an ED25519PrivateKey instance
    :returns: the ASN.1 encoding as a byte string
    """
    encoded_len = _lib.xtt_asn1_private_key_length()
    encoded = _ffi.new('unsigned char[]', encoded_len)
    rc = _lib.xtt_asn1_from_ed25519_private_key(priv_key.native, encoded, len(encoded))
    if rc == RC.SUCCESS:
        return _ffi.buffer(encoded)[:]
    else:
        raise error_from_code(rc)
