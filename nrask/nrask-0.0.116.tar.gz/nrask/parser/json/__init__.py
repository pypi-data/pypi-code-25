# -*- coding: utf-8 -*-
from simplejson import dumps,loads

__all__ = [
    'dictfy',
    'jsonify'
]

def dictfy(_):
    try:
        return loads(_)
    except:
        return False

def jsonify(_):
    try:
        return dumps(_)
    except:
        return False
