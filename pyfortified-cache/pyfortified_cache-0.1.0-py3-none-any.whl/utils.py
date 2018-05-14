#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import ujson as json

def create_hash_key(key):
    if key is None:
        raise ValueError("Parameter 'key' not defined.")

    if isinstance(key, str):
        key_str = key
    if isinstance(key, dict):
        key_str = json.dumps(key, sort_keys=True)

    return hashlib.md5(key_str.encode('utf-8')).hexdigest()