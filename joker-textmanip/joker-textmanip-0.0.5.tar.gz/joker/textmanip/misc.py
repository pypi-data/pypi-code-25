#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, print_function

import random

from string import digits, ascii_letters, ascii_uppercase


# http://www.garykessler.net/library/base64.html
b64_chars = digits + ascii_letters + '+/'
b64_urlsafe_chars = ascii_letters + digits + '_-'
b32_chars = ascii_uppercase + '234567'


def random_string(length, chars=None):
    if not chars:
        chars = digits + ascii_letters
    return ''.join(random.choice(chars) for _ in range(length))


# https://unicode-table.com/en/blocks/cjk-unified-ideographs/
