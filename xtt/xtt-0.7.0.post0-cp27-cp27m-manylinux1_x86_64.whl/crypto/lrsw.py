from __future__ import absolute_import
from __future__ import print_function

from xtt._ffi_utils import DataStruct

__all__ = [
    'LRSWCredential', 'LRSWPrivateKey', 'LRSWGroupPublicKey',
    'LRSWPseudonym'
]

class LRSWCredential(DataStruct):
    struct = "xtt_daa_credential_lrsw"

class LRSWPrivateKey(DataStruct):
    struct = "xtt_daa_priv_key_lrsw"

class LRSWGroupPublicKey(DataStruct):
    struct = "xtt_daa_group_pub_key_lrsw"

class LRSWPseudonym(DataStruct):
    struct = "xtt_daa_pseudonym_lrsw"
