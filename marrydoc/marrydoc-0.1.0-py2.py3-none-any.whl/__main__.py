# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2018 Daniel Mark Gass
#
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
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""marrydoc command line interface."""

from __future__ import absolute_import, division, print_function, unicode_literals

import importlib
import os
import sys
from argparse import ArgumentParser, SUPPRESS
from glob import glob
from subprocess import Popen, PIPE, STDOUT

from ._script import Mode, Script


def main(args=None):
    """Command line interface.

    :param list args: command line args (default is sys.argv)

    """
    parser = ArgumentParser(
        prog='marrydoc',
        description='Ensure related docstrings are consistent.')

    parser.add_argument(
        'path', nargs='+',
        help='module or directory path')

    parser.add_argument(
        '-m', '--merge', action='store_true',
        help='update module docstrings')

    parser.add_argument(
        '-w', '--walk', action='store_true',
        help='recursively walk directories')

    parser.add_argument(
        '--evaluate', action='store_true', help=SUPPRESS)

    parser.add_argument(
        '--test', action='store_true', help=SUPPRESS)

    args = parser.parse_args(args)

    if args.evaluate:
        # This is a special invocation to check one specific Python script.
        # The normal command line interface re-invokes the command line
        # interface (with --evaluate) with a fresh interpreter for each Python
        # script to check.

        assert len(args.path) == 1

        # activate marrydoc decorator functionality (the marrydoc decorators
        # that the Python script being checked uses are effected by this
        # monkey patching)
        if args.merge:
            Script.mode = Mode.MERGE
        else:
            Script.mode = Mode.CHECK
        Script.test_mode = args.test
        Script.path_of_interest = args.path[0]

        # import Python script to check (marrydoc decorators record mismatches)
        dirpath, filename = os.path.split(Script.path_of_interest)
        modulename = os.path.splitext(filename)[0]
        sys.path[0:0] = [dirpath]
        importlib.import_module(modulename)

        # look for any mismatches, report and take action if necessary
        exitcode = Script.check_files_for_mismatches()

    else:
        # determine the list of Python scripts and subdirectories (to search)
        dir_paths = []
        file_paths = []
        for pattern in args.path:
            paths = glob(pattern)
            if not paths:
                print('ERROR: {!r} not found'.format(pattern))
                return 1
            for path in paths:
                if os.path.isdir(path):
                    dir_paths.append(path)
                elif path.endswith('.py'):
                    file_paths.append(path)
                else:
                    print(
                        'ERROR: {!r} invalid '
                        '(does not specify directory or .py file)'.format(pattern))
                    return 1

        # search subdirectories for Python scripts to process
        if args.walk:
            for dirpath in dir_paths:
                for root, _dirs, files in os.walk(dirpath):
                    file_paths += [os.path.join(root, name) for name in files]
        else:
            for dirpath in dir_paths:
                file_paths += [
                    os.path.join(dirpath, name) for name in os.listdir(dirpath)]

        # filter out files from subdirectory scan that are not .py
        file_paths = sorted(
            os.path.abspath(path) for path in file_paths if path.endswith('.py'))

        # determine arguments to call this command line interface again with
        # a fresh interpreter to evaluate a single Python script
        sub_args = [sys.executable, '-m', 'marrydoc', '--evaluate']
        if args.merge:
            sub_args.append('--merge')
        if args.test:
            sub_args.append('--test')

        # For each Python script, check it by re-invoking this command line
        # tool with a fresh interpreter with the --evaluate switch. This may
        # be more inefficient, but is a simple way to exactly control the
        # order in which scripts are evaluated, the order in which results
        # are presented, and guarantees no problems evaluating similarly named
        # scripts (this last point might be an irrational fear).
        exitcode = Script.OK_STATUS
        for path in file_paths:
            # use Popen to capture STDOUT and print it so that regression
            # test may redirect sys.stdout to evaluate it
            p = Popen(sub_args + [path], stdin=PIPE, stdout=PIPE, stderr=STDOUT,
                      universal_newlines=True)
            stdout, _stderr = p.communicate()
            print(stdout, end='')

            if p.returncode != Script.OK_STATUS:
                exitcode = p.returncode
                if p.returncode != Script.MISMATCH_STATUS:
                    break

    return exitcode


if __name__ == '__main__':

    sys.exit(main())
