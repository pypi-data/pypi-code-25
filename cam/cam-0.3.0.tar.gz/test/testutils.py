import os
import sys
import platform
import unittest
import argparse


class TestCase( unittest.TestCase ):
    _DATA_DIRECTORY = os.path.normpath(
        os.path.abspath( os.path.join( 
            os.path.dirname(__file__), 'data')))

    def __init__(self,methodName ='runTest'):
        unittest.TestCase.__init__(self,methodName)

    def assertPathEqual(self, first, second, msg=None):
        """Fail if the two path are not same one.
        """
        first = os.path.normpath(os.path.abspath(first) ).replace('\\','/')
        second = os.path.normpath(os.path.abspath(second) ).replace('\\','/')
        if platform.system() == 'Windows':
            first = os.path.normcase(first)
            second = os.path.normcase(second)
            

        assertion_func = self._getAssertEqualityFunc(first, second)
        assertion_func(first, second, msg=msg)

    def pathOf(self, rpath, base = 'data'):
        if base == 'data':
            return os.path.normpath( os.path.abspath(
                    os.path.join(self._DATA_DIRECTORY,rpath)))

    

    def dispatch(self,argv):
        parser = argparse.ArgumentParser(prog="cam")


        parser.add_argument(
            "command",
            choices=["build"],
        )
        parser.add_argument(
            "args",
            help=argparse.SUPPRESS,
            nargs=argparse.REMAINDER,
        )

        args = parser.parse_args(argv)
        main = None
        import cam
        import cam.commands
        import cam.commands.build

        if args.command == 'build':
            main = cam.commands.build.main
            
        main(args.args )



