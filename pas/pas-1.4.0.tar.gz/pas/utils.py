# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 bindh3x <os@bindh3x.io>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

import sys
import os
import json
import string
import random

from datetime import datetime
from click import style, prompt

def error(text, exit=False, code=None):
    """Print error message and exit if specified with ``code``."""
    sys.stdout.write("{} {}\n".format(style("error:",
                                                  fg="red"), text))
    if exit:
        sys.exit(code)

def print_warning(text, exit=False, code=None):
    """Print error message and exit if specified with ``code``."""
    sys.stdout.write("{} {}\n".format(style("warning:",
                                                  fg="yellow"), text))
    if exit:
        sys.exit(code)

# XXX: Move to manager.py at some point.
def repl(suffix="> ", account=None):
    """Repl interface implementation."""
    account = account if account else {'__metadata__': {'keys': {}}}

    while True:
        try:
            key = prompt(prompt_suffix=suffix, text="key ")
            value = prompt(prompt_suffix=suffix, text="value({}) ".format(style(key, fg="red")))
            if value.startswith("gen-pass") and len(value.split()) == 2:
                if value.split()[1].isdigit():
                    value = generate_password(int(value.split()[1]))
                else:
                    error("please specify password length (gen-pass <length>).")
                    continue
        except Exception as e:
            error(e)
            break
        account.update({key: value})
        account['__metadata__']['keys'].update({key: {'modified': datetime.now().timestamp()}})
        print_account(account)

    return account

def print_account(data):
    """Print the account without the __metadata__ entry."""
    _ = data.copy()
    # XXX: for Pas < 1.0.
    if _.__contains__('__metadata__'):
        _.pop('__metadata__')
    print(json.dumps(_, indent=2, sort_keys=True))

def which(name):
    """Using which(1) or any other method to locate binary

    in Unix is not portable.
    """
    # if os.environ.__contains__("PATH")
    path = os.getenv("PATH")

    for _ in path.split(":"):
        bin_path = "{}/{}".format(_, name)
        if os.path.exists(bin_path):
            return bin_path
    return None

# FIXME: Better implementation. (read from /dev/urandom).
def generate_password(length):
    """Generates random password."""
    characters = string.printable[0:62] + "!#$&()*+,-.:;<=>?@[]^_{|}]"
    return ''.join(random.choices(characters, k=length))
