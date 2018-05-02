#!/usr/bin/env python

import sys
import json
import re

name_re = re.compile('^([a-zA-Z_][a-zA-Z0-9_]*)=(.*)$')

def decode_s(s):
    try:
        return json.loads(s)
    except:
        return s

def nclf(argv):
    args_pos = []
    args_named = {}

    for arg in argv:
        m = name_re.match(arg)
        if m is not None:
            x = m.groups()
            name = x[0]
            value = x[1]
            args_named[name] = decode_s(value)
        else:
            value = decode_s(arg)
            args_pos.append(value)

    return [args_pos, args_named]

if __name__ == '__main__':
    args = nclf(sys.argv[1:])
    print(json.dumps(args))
