from __future__ import absolute_import
from __future__ import print_function

from enum import IntEnum

from xtt._ffi import ffi as _ffi
from xtt._ffi import lib as _lib
from xtt._ffi_utils import DataStruct

__all__ = [
    'asn1', 'certificates', 'client', 'crypto', 'exceptions',
    'server', 'socket',
    'Version', 'SuiteSpec', 'SignatureType', 'Identity', 'GroupId'
]

class Version(IntEnum):
    ONE = _lib.XTT_VERSION_ONE

class SuiteSpec(IntEnum):
    XTT_X25519_LRSW_ED25519_CHACHA20POLY1305_SHA512  = _lib.XTT_X25519_LRSW_ED25519_CHACHA20POLY1305_SHA512
    XTT_X25519_LRSW_ED25519_CHACHA20POLY1305_BLAKE2B = _lib.XTT_X25519_LRSW_ED25519_CHACHA20POLY1305_BLAKE2B
    XTT_X25519_LRSW_ED25519_AES256GCM_SHA512         = _lib.XTT_X25519_LRSW_ED25519_AES256GCM_SHA512
    XTT_X25519_LRSW_ED25519_AES256GCM_BLAKE2B        = _lib.XTT_X25519_LRSW_ED25519_AES256GCM_BLAKE2B

class SignatureType(IntEnum):
    ED25519 = _lib.XTT_SERVER_SIGNATURE_TYPE_ED25519

class Identity(DataStruct):
    struct = "xtt_identity_type"

class GroupId(DataStruct):
    struct = "xtt_group_id"

from xtt.asn1 import *
from xtt.certificates import *
from xtt.client import *
from xtt.crypto import *
from xtt.exceptions import *
from xtt.server import *
from xtt.socket import *
