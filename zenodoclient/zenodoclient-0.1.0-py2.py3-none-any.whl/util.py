# coding: utf8
from __future__ import unicode_literals, print_function, division
import hashlib


def md5(p, bufsize=32768):
    hash_md5 = hashlib.md5()
    with p.open('rb') as fp:
        for chunk in iter(lambda: fp.read(bufsize), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
