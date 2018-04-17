#
# Copyright (c) 2012, 2014
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# License: MIT/X11
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE
#
import smbc
from shutil import copyfileobj
from coils.core.logic import ActionCommand


class SMBGetFileAction(ActionCommand):
    """
    Retrieve a file from an SMB/CIFS file server to a message
    """
    __domain__ = "action"
    __operation__ = "smb-get-file"
    __aliases__ = ['smbGetFile', 'smbGetFileAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return self._mimetype

    def authentication_callback(
        self, server, share, workgroup, username, password,
    ):
        return (
            self._domain_string, self._username_string, self._password_string,
        )

    def do_action(self):
        cifs = smbc.Context(auth_fn=self.authentication_callback)
        handle = cifs.open(self._source_unc)
        copyfileobj(handle, self._wfile)
        handle.close()

    def parse_action_parameters(self):
        self._domain_string = self.process_label_substitutions(
            self.action_parameters.get('domain')
        )
        self._password_string = self.process_label_substitutions(
            self.action_parameters.get('password')
        )
        self._username_string = self.process_label_substitutions(
            self.action_parameters.get('username')
        )
        self._source_unc = self.process_label_substitutions(
            self.action_parameters.get('source')
        )
        self._mimetype = self.process_label_substitutions(
            self.action_parameters.get('mimetype', 'application/octet-stream')
        )

    def do_epilogue(self):
        pass
