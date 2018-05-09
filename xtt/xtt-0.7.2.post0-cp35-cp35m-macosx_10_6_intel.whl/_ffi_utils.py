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

import six
import sys

from xtt._ffi import ffi as _ffi
from xtt._ffi import lib as _lib

from xtt._utils import to_bytes, to_text, _check_len

class _DataStructMetaclass(type):
    """
    Adds a :sizeof: class member containing the size in bytes of the
    native struct.
    """

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, 'struct'):
            raise ValueError("Child class must define 'struct'")
        cls.sizeof = _ffi.sizeof(cls.struct)

        return type.__call__(cls, *args, **kwargs)

@six.add_metaclass(_DataStructMetaclass)
class DataStruct(object):
    """
    Many XTT structs are wrappers for a single char[] named data. This
    base class hodls a native struct and provides access to the
    underlying data array.

    Child classes must set the `struct` class member to specify
    the struct to wrap.
    """
    __metaclass__ = _DataStructMetaclass

    @classmethod
    def from_file(cls, filename):
        with open(filename, 'rb') as f:
            raw = f.read()
            return cls(raw)

    def __init__(self, value=None):
        self.native = _ffi.new('%s*'%self.struct)

        if self.native == _ffi.NULL:
            raise MemoryError("Unable to allocate native object")

        if value:
            self.data = value

    def __repr__(self):
        return "%s(%s)"%(type(self).__name__, repr(self.data))

    def __str__(self):
        return str(self.data)

    @property
    def data(self):
       return _ffi.buffer(self.native.data)[:]

    @data.setter
    def data(self, value):
        _check_len(self.native.data, value)
        _ffi.memmove(self.native.data, value, len(value))

class Buffer(object):
    """
    Owns and allocates an underlying C unsigned char buffer.
    """

    def __init__(self, size):
        self.size = size
        self.native = _ffi.new('unsigned char[]', self.size)

        if self.native == _ffi.NULL:
            raise MemoryError("Unable to allocate native object")

class BufferView(object):
    """
    A view of an existing underlying C unsigned char buffer.

    The view is defined by two parameters, an unsigned char
    pointer and a size. These may be set directly or pointers
    to them may be passed as outputs to C functions.

    This class is designed to work with the :io_bytes_requested:
    and :io_ptr: parameters of the XTT C functions.
    """

    def __init__(self):
        self._size = _ffi.new('uint16_t[1]')
        self._data = _ffi.new('unsigned char *[1]')

        if self._size == _ffi.NULL or self._data == _ffi.NULL:
            raise MemoryError("Unable to allocate native object")

    @property
    def buffer(self):
        """
        A Python buffer representing the underlying memory.

        The buffer may be passed to IO functions like this:
        `view.buffer = socket.recv(len(view.buffer))`
        """
        return _ffi.buffer(self._data[0], self._size[0])

    @property
    def addressof_size(self):
        return _ffi.addressof(self._size)[0]

    @property
    def addressof_data(self):
        return _ffi.addressof(self._data)[0]

    @property
    def size(self):
        return self._size[0]

    @property
    def data(self):
        return self._data[0]
