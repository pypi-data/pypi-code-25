#!/usr/bin/env python3
'''
Created on Jan 2, 2018

@author: arnon
'''

from subprocess import run, PIPE


def install_required(exact=False):
    cmd = ['pip', 'freeze']
    result = run(cmd, shell=False, stdout=PIPE, stderr=PIPE)

    if result.returncode != 0:
        raise RuntimeError("Failed pip freeze: {}".format(result.stderr))

    relations = ">=" if not exact else "=="
    items = []
    for item in result.stdout.decode().split('\n'):
        item = item.strip()
        if item:
            package, _, version = item.partition('==')
            items += ["{}{}{}".format(package, relations, version)]

    return items


def format_setup_required(required, ident=''):
    items = []
    prefix = '{}install_required = ['.format(ident)
    plen = len(prefix) + len(ident)
    for item in required:
        items += ["{}'{}',".format(prefix, item)]
        prefix = ' ' * plen
    items += [']']
    return '\n'.join(items)


def format_file_required(required, file='REQUIRED'):
    with open(file, 'w') as f:
        for require in required:
            f.write("{}\n".format(require))


