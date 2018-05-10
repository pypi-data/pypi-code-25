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

import subprocess
from pas.utils import which

class GnuPGError(Exception):
    """GnuPG Exceptions handler"""
    pass

class GnuPG(object):
    """Tiny Python binding for GnuPG."""
    def __init__(self, homedir=None):
        self.homedir = homedir
        self.gpg_path = self._get_gpg_path()

    @staticmethod
    def _get_gpg_path():
        """Get the path of the GPG binary."""
        path = which("gpg")
        if not path:
            raise GnuPGError("GnuPG is not found.")
        return path

    def _execute_file(self, arguments=None):
        """Execute the actual command for file oprations."""
        command = "{} --homedir '{}' {} 2> /dev/null".format(self.gpg_path, self.homedir, arguments)
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return stdout, stderr

    def _execute(self, arguments=None, data=None):
        """Execute the actual command for stdin/stdout oprations.

        :param data: data to write to stdin.
        """
        command = "{} --homedir '{}' {}".format(self.gpg_path, self.homedir, arguments)
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        stdout, stderr = process.communicate(input=data)
        return stdout, stderr

    def decrypt_file(self, filename, recipient, output=None):
        """Decrypt filename."""
        arguments = "--output '{}' --decrypt -r '{}' {}".format(output, recipient, filename)
        if not output:
            arguments = "--decrypt -r '{}' {}".format(recipient, filename)
        return self._execute_file(arguments=arguments)

    def encrypt_file(self, filename, recipient, output=None):
        """Encrypt filename."""
        arguments = "--output '{}' --encrypt -r '{}' {}".format(output, recipient, filename)
        if not output:
            arguments = "--encrypt -r '{}' {}".format(recipient, filename)
        return self._execute_file(arguments=arguments)

    def encrypt(self, data, recipient, output=None, overwrite=False):
        """Encrypt data.

        :param overwrite: overwrite the output file.
        """
        if overwrite:
            arguments = "--batch --yes --output {} --encrypt -r '{}'".format(output, recipient)
        else:
            arguments = "--output {} --encrypt -r '{}'".format(output, recipient)
        return self._execute(arguments, data=data)

    def decrypt(self, data, recipient, output=None, overwrite=False):
        """Decrypt data."""
        if overwrite:
            arguments = "--batch --yes --output {} --decrypt -r '{}'".format(output, recipient)
        else:
            arguments = "--output {} --decrypt -r {}".format(output, recipient)
        return self._execute(arguments, data=data)

__all__ = [ GnuPG.__name__ ]
