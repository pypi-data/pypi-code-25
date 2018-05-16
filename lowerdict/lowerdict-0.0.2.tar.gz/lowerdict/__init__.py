#!/usr/bin/env python
from isstring import isstring
from public import public


@public
def lowerdict(*args, **kwargs):
    inputdict = dict(*args, **kwargs)
    resultdict = dict()
    for key, value in inputdict.items():
        if isstring(key):
            key = key.lower()
        resultdict[key] = value
    return resultdict
