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
import string
import json
import re
import pas.pyperclip

from time import sleep
from datetime import datetime
from click import style
from pas.gnupg import GnuPG
from pas.utils import repl, print_account, error, print_warning

PAS_HOME = os.getenv("PAS_HOME", os.path.expanduser("~/.config/pas"))
PAS_GPG_HOME = os.getenv("PAS_GPG_HOME", os.path.expanduser("~/.gnupg"))
PAS_SAFE = os.getenv("PAS_SAFE", os.path.join(PAS_HOME, "safe.gpg"))
PAS_GPG_RECIPIENT = os.getenv("PAS_GPG_RECIPIENT", "nobody")
PAS_CLIPBOARD = os.getenv("PAS_CLIPBOARD", "xsel")
PAS_CLIPBOARD_CLEAR_TIME = os.getenv("PAS_CLIPBOARD_CLEAR_TIME", 7)

class Pas(object):
    """Secure Password manager"""
    def __init__(self, options):
        self.options = options
        self.gpg = GnuPG(homedir=PAS_GPG_HOME)
        self.safe = self._safe_unlock()

    def _safe_create(self):
        """Create empty safe."""
        if not os.path.exists(PAS_HOME):
            os.makedirs(PAS_HOME)
        self.gpg.encrypt(data=b'{}',
                         recipient=PAS_GPG_RECIPIENT,
                         output=PAS_SAFE)

    def _safe_unlock(self):
        """Unlock the safe and return the data."""
        if not os.path.exists(PAS_HOME):
            self._safe_create()
        safe, err = self.gpg.decrypt_file(filename=PAS_SAFE,
                                          recipient=PAS_GPG_RECIPIENT)
        if not safe:
            error("failed to open the safe.", exit=True, code=1)
        return json.loads(safe)

    def _account_exists(self, name):
        """Check if account exists in the safe."""
        return self.safe.__contains__(name)

    def _account_key_exists(self, name, key):
        """Check if key exists in account."""
        return self.safe[name].__contains__(key)

    def read(self):
        """Read account data."""
        if not self._account_exists(self.options['account']):
            error("'{}' doesn't exists.".format(self.options['account']),
                                                exit=True,
                                                code=1)
        if self.options['key']:
            if not self._account_key_exists(self.options['account'], self.options['key']):
                error("there is no '{}' in '{}'.".format(self.options['key'],
                    self.options['account']), exit=True, code=1)
            value = self.safe[self.options['account']][self.options['key']]

            if self.options['key'] == "password":
                timestamp = self.safe[self.options['account']]['__metadata__']['keys'][self.options['key']]['modified']
                now = datetime.now().timestamp()
                days = int((now - timestamp) / (60 * 60 * 24))
                # Warn the user if is password is 1 month old.
                if days > 31:
                    print_warning("you last update your password {} days ago.".format(days))

            # Copy to clipboard and clear after ``PAS_CLIPBOARD_CLEAR_TIME``.
            # this security feautre enabled by default, because I want
            # to encourage users to use it, it's safer and will
            # ensure that:
            #   A. you will not paste your password by mistake.
            #   B. it will not be recoverable from the clipboard after ``PAS_CLIPBOARD_CLEAR_TIME``.
            #
            if not self.options['no_clipboard']:
                pas.pyperclip.set_clipboard(PAS_CLIPBOARD)
                pas.pyperclip.copy(value, primary=True)
                for s in range(PAS_CLIPBOARD_CLEAR_TIME):
                    print("\rwiping clipboard in {} ...".format(PAS_CLIPBOARD_CLEAR_TIME - s),
                                                                end='')
                    sleep(1)
                pas.pyperclip.clear(primary=True)
                sys.stdout.write('\n')
            else:
                print(key)
        else:
            print_account(self.safe[self.options['account']])

    def add(self):
        """Add new account or key."""
        account = None

        if self._account_exists(self.options['account']):
            account = self.safe[self.options['account']]
        account = repl(account=account)
        self.safe[self.options['account']] = account

        # Save the modifications.
        self.gpg.encrypt(data=bytes(json.dumps(self.safe).encode()),
            recipient=PAS_GPG_RECIPIENT,
            output=PAS_SAFE, overwrite=True)

    def delete(self):
        """Delete key or account from the safe."""
        if not self._account_exists(self.options['account']):
            error("account '{}' doesn't exists.".format(self.options['account']),
                                                        exit=True,
                                                        code=1)

        if self.options['key']:
            if self._account_key_exists(self.options['account'], self.options['key']):
                self.safe[self.options['account']].pop(self.options['key'])
        else:
            self.safe.pop(self.options['account'])

        # Save the modifications
        self.gpg.encrypt(data=bytes(json.dumps(self.safe).encode()),
            recipient=PAS_GPG_RECIPIENT,
            output=PAS_SAFE, overwrite=True)

    def search(self):
        """Search account or key."""
        match = [ _ for _ in self.safe if re.findall(self.options['query'], _) ]
        query = re.sub('[^A-Za-z0-9]+', '', self.options['query'])

        for _ in match:
            print(_.replace(query, style(query, fg="red", bg="white"), 1))

    def stats(self):
        """Print safe stats."""
        print("{} accounts.".format(len(self.safe)))
