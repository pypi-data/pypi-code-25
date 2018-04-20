"""Module to expose resources through a command-line interface."""

# Copyright © 2018 Paul Bryan.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

class Shell:
    """TODO: Description."""

    def __init__(self, *, prompt="> ", resources={}):
        """TODO: Description."""
        super().__init__()
        self.prompt = prompt
        self.resources = resources
        self._looping = False
        self.commands = {"help": self.help, "quit": self.quit}

    def loop(self):
        """Repeatedly issue a command prompt and process input."""
        if self._looping:
            raise SomeError("already looping")
        self._looping = True
        try:
            while self._looping:
                try:
                    self.process(input(self.prompt))
                except EOFError:
                    break
        finally:
            self._looping = False

    def process(self, line):
        """Process a single command line."""
        print(line)

    def help(self):
        pass

    def quit(self):
        pass

"""
resource method [params]
help [resource [method]]
quit
"""
