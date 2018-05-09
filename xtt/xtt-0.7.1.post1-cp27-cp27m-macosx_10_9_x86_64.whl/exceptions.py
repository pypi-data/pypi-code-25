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
from xtt._ffi_utils import to_bytes, to_text, DataStruct

__all__ = [
    'error_string', 'ReturnCode',
    'XTTError', 'XTTWantWriteError', 'XTTWantReadError',
    'XTTWantBuildServerAttestError', 'XTTWantPreparseServerAttestError',
    'XTTWantBuildIdClientAttestError', 'XTTWantPreparseIdClientAttestError',
    'XTTWantVerifyGroupSignatureError', 'XTTWantBuildIdServerFinishedError',
    'XTTWantParseIdServerFinishedError', 'XTTWantParseIdServerFinishedError'
]

def _build_return_code_enum():
    """
    Creates an IntEnum containing all the XTT return codes.

    Finds all return codes by scanning the FFI for items whose names match
    the pattern "XTT_RETURN_<X>".  The name of the result enum value is the
    suffix "<X>".
    """
    prefix = 'XTT_RETURN_'
    codes = {k[len(prefix):]:v for (k, v) in vars(_lib).items() if k.startswith(prefix)}
    return IntEnum('ReturnCode', codes)

ReturnCode = _build_return_code_enum()

def error_string(rc):
    data = _lib.xtt_strerror(rc)
    return to_text(_ffi.string(data))

class XTTError(Exception):
    """
    Raised to signal an error from the XTT library.

    The :code: instance member contains the actual error code.
    """

    def __init__(self, code, *args):
        self.code = code
        self.msg = error_string(code)
        super(Exception, self).__init__(self.code, self.msg, *args)

class XTTWantError(Exception):
    """
    Raised to signal that the application needs to perform some work before
    the XTT library can continue.
    """

    def __init__(self, *args):
        super(XTTWantError, self).__init__(self._WANT, *args)

class XTTWantWriteError(XTTWantError):
    _WANT = ReturnCode.WANT_WRITE

class XTTWantReadError(XTTWantError):
    _WANT = ReturnCode.WANT_READ

class XTTWantBuildServerAttestError(XTTWantError):
    _WANT = ReturnCode.WANT_BUILDSERVERATTEST

class XTTWantPreparseServerAttestError(XTTWantError):
    _WANT = ReturnCode.WANT_PREPARSESERVERATTEST

class XTTWantBuildIdClientAttestError(XTTWantError):
    _WANT = ReturnCode.WANT_BUILDIDCLIENTATTEST

class XTTWantPreparseIdClientAttestError(XTTWantError):
    _WANT = ReturnCode.WANT_PREPARSEIDCLIENTATTEST

class XTTWantVerifyGroupSignatureError(XTTWantError):
    _WANT = ReturnCode.WANT_VERIFYGROUPSIGNATURE

class XTTWantBuildIdServerFinishedError(XTTWantError):
    _WANT = ReturnCode.WANT_BUILDIDSERVERFINISHED

class XTTWantParseIdServerFinishedError(XTTWantError):
    _WANT = ReturnCode.WANT_PARSEIDSERVERFINISHED

_by_codes = {
    ReturnCode.WANT_WRITE : XTTWantWriteError,
    ReturnCode.WANT_READ : XTTWantReadError,
    ReturnCode.WANT_BUILDSERVERATTEST : XTTWantBuildServerAttestError,
    ReturnCode.WANT_PREPARSESERVERATTEST : XTTWantPreparseServerAttestError,
    ReturnCode.WANT_BUILDIDCLIENTATTEST : XTTWantBuildIdClientAttestError,
    ReturnCode.WANT_PREPARSEIDCLIENTATTEST : XTTWantPreparseIdClientAttestError,
    ReturnCode.WANT_VERIFYGROUPSIGNATURE : XTTWantVerifyGroupSignatureError,
    ReturnCode.WANT_BUILDIDSERVERFINISHED : XTTWantBuildIdServerFinishedError,
    ReturnCode.WANT_PARSEIDSERVERFINISHED : XTTWantParseIdServerFinishedError,
}

def error_from_code(code):
    """
    Returns an XTTError instance for the return code value.
    """
    if code in _by_codes:
        return _by_codes[code]
    else:
        return XTTError(code)
