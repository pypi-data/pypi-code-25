#!/usr/bin/env python
from public import public


@public
def slicedict(d, keys):
    result = dict()
    for k in keys:
        if k in d:
            result[k] = d[k]
    return result
