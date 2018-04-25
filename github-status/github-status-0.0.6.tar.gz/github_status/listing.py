from __future__ import print_function
import sys


class List(object):

    _help = """
List all status(es) for a given commit (sha).

Not implemented yet
    """

    def __init__(self, argv=None, parse=True):
        if argv is None:
            argv = sys.argv
        if parse:
            self.main(argv)

    def help(self):
        return self._help

    def main(self, argv):
        print(self.help())
        return
