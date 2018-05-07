# coding: utf-8

from ._siphash import lib

def siphash24(key: bytes, data: bytes):
    return lib.siphash24(data, len(data), key).to_bytes(8, 'big')
