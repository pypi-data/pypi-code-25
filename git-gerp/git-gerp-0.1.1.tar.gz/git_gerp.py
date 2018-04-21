#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Git grep wrapper for arguments re-ordering, that can use options after filenames
#
# Usage: git-gerp [<git-grep-argument>...]
#
# Copyright (c) 2018 htaketani <h.taketani@gmail.com>
# This software is released under the MIT License.
import sys
import re
import subprocess

# git grep command
COMMAND = ['git', 'grep']

# git grep options that require a parameter
OPTS_WITH_PARAM = ['--max-depth', '--open-files-in-pager', '--context', '--after-context', '--before-context', '--threads', '-O', '-C', '-A', '-B', '-f', '-e']

def is_double_dash(token):
    return token == '--'

def is_opt(token):
    return is_long_opt(token) or is_short_opt(token) or is_group_opt(token)

def is_long_opt(token):
    return re.match(r'^--.+', token)

def is_short_opt(token):
    return re.match(r'^-\w+$', token)

def is_group_opt(token):
    return token in ['(', ')']

def is_long_opt_without_param(token):
    return is_long_opt(token) and ('=' not in token)

def tail_short_opt(token):
    return '-' + token[-1]

def requires_param(token):
    opt = token if is_long_opt_without_param(token) else tail_short_opt(token) if is_short_opt(token) else None
    return opt in OPTS_WITH_PARAM

def replace_args(args):
    args = args[:]
    opt_args = []   # option (and parameter) args
    plain_args = [] # non-option args
    while len(args):
        token = args.pop(0)
        if is_double_dash(token):
            plain_args.append(token)
            plain_args.extend(args)
            break;
        elif is_opt(token):
            opt_args.append(token)
            if requires_param(token) and len(args):
                opt_args.append(args.pop(0))
        else:
            plain_args.append(token)
    return opt_args + plain_args

def git_gerp(args):
    replaced_args = replace_args(args)
    return subprocess.call(COMMAND + replaced_args)

def main():
    args = sys.argv[1:]
    rc = git_gerp(args)
    sys.exit(rc)

if __name__ == '__main__':
    main()
