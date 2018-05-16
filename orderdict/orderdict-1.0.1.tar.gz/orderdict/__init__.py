#!/usr/bin/env python
from collections import OrderedDict
from public import public


@public
def orderdict(ordering, *args, **kwargs):
    inputdict = OrderedDict(*args, **kwargs)
    resultdict = OrderedDict()
    if not ordering:
        ordering = []
    for key in ordering:
        if key in inputdict:
            resultdict[key] = inputdict[key]
    for key in inputdict.keys():
        if key not in resultdict:
            resultdict[key] = inputdict[key]
    return resultdict
