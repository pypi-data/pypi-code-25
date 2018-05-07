# coding: utf-8

import os

from cffi import FFI

siphash_source_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'SipHash.cpp')

ffibuilder = FFI()
ffibuilder.cdef('''uint64_t siphash24(const void *src, unsigned long src_sz, const char key[16]);''')
siphash_source = open(siphash_source_file)
ffibuilder.set_source('csiphash24._siphash', siphash_source.read(), source_extension='.cpp')

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
