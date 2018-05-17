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
