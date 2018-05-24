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


def evaluate(path, modulename, merge, test_mode):
    """Evaluate docstrings in a single module.

    :param str path: module file path
    :param str modulename: importable module name (`None` if not known)
    :param bool merge: perform update/merge if required
    :param bool test_mode: internal regression test mode
    :returns: exit code
    :rtype: int

    """
    # activate marrydoc decorator functionality (the marrydoc decorators
    # that the Python script being checked uses are effected by this
    # monkey patching)
    if merge:
        Script.mode = Mode.MERGE
    else:
        Script.mode = Mode.CHECK
    Script.test_mode = test_mode
    Script.path_of_interest = path

    # import Python script to check (marrydoc decorators record mismatches)
    if modulename is None:
        dirpath, filename = os.path.split(Script.path_of_interest)
        modulename = os.path.splitext(filename)[0]
        sys.path[0:0] = ['.']
        cwd = os.getcwd()
        os.chdir(dirpath)
        try:
            importlib.import_module(modulename)
        finally:
            os.chdir(cwd)
    else:
        importlib.import_module(modulename)

    # look for any mismatches, report and take action if necessary
    return Script.get_instance(path).check_for_mismatches()


def sort_paths(paths):
    """Separate file and directory paths from importable names.

    :params paths: file system paths and importable names
    :type paths: list of str
    :returns: (file paths, directory paths, importable names)
    :rtype: tuple of (list of str, list of str, list of str)

    """
    file_paths = []
    dir_paths = []
    importable_names = []

    for pattern in paths:
        pattern_paths = glob(pattern)
        if pattern_paths:
            for path in pattern_paths:
                if os.path.isdir(path):
                    dir_paths.append(path)
                elif path.lower().endswith('.py'):
                    file_paths.append(path)
        else:
            importable_names.append(pattern)

    return file_paths, dir_paths, importable_names


def scan_directories(dir_paths, walk):
    """Search directories for Python scripts to process.

    :param dir_paths: directories
    :type dir_paths: list of str
    :param bool walk: recurse through subdirectories
    :returns: python script file paths
    :rtype: list of str

    """
    file_paths = []

    if walk:
        for dirpath in dir_paths:
            for root, _dirs, files in os.walk(dirpath):
                if '__pycache__' not in root:
                    file_paths += [os.path.join(root, name) for name in files]
    else:
        for dirpath in dir_paths:
            file_paths += [
                os.path.join(dirpath, name) for name in os.listdir(dirpath)]

    return [path for path in file_paths if path.lower().endswith('.py')]


def _get_module_path(path):
    return os.path.abspath(path.replace('.pyc', '.py').replace('.PYC', '.PY'))


def resolve_importable_names(names, walk):
    """Determine module names to scan and their associated path.

    :param names: module/package names
    :type names: list of str
    :param bool walk: recursively walk subpackages
    :returns: dict of path:module name associations of those to scan
    :rtype: dict of str:str

    """
    to_evaluate = {}

    for name in names:
        importable = importlib.import_module(name)

        to_evaluate[_get_module_path(importable.__file__)] = name

        if walk:
            try:
                pkg_path = importable.__path__[0]
            except AttributeError:
                pass
            else:
                for root, _dirs, files in os.walk(pkg_path):
                    if '__pycache__' in root:
                        continue

                    subpkg_relpath = os.path.relpath(root, pkg_path)

                    if subpkg_relpath == '.':
                        subpkg = [name]
                    else:
                        subpkg = [name] + subpkg_relpath.split(os.sep)

                    for filename in files:
                        if filename.lower().endswith('.py'):
                            path = _get_module_path(os.path.join(root, filename))
                            if filename.startswith('__init__.'):
                                to_evaluate[path] = '.'.join(subpkg)
                            else:
                                to_evaluate[path] = '.'.join(
                                    subpkg + [os.path.splitext(filename)[0]])

    return to_evaluate


def main(args=None):
    """Command line interface.

    :param list args: command line args (default is sys.argv)

    """
    parser = ArgumentParser(
        prog='marrydoc',
        description='Ensure related docstrings are consistent.')

    parser.add_argument(
        'paths', nargs='+', metavar='path',
        help='module/package name or path')

    parser.add_argument(
        '-m', '--merge', action='store_true',
        help='update module docstrings')

    parser.add_argument(
        '-w', '--walk', action='store_true',
        help='recursively walk directories')

    parser.add_argument(
        '--evaluate', action='store_true', help=SUPPRESS)

    parser.add_argument(
        '--modulename', help=SUPPRESS)

    parser.add_argument(
        '--test', action='store_true', help=SUPPRESS)

    args = parser.parse_args(args)

    if args.evaluate:
        # This is a special invocation to check one specific Python script.
        # The normal command line interface re-invokes the command line
        # interface (with --evaluate) with a fresh interpreter for each Python
        # script to check.
        assert len(args.paths) == 1

        exitcode = evaluate(args.paths[0], args.modulename, args.merge, args.test)
    else:
        file_paths, dir_paths, importable_names = sort_paths(args.paths)

        file_paths += scan_directories(dir_paths, args.walk)

        to_evaluate = {os.path.abspath(path): None for path in file_paths}

        to_evaluate.update(resolve_importable_names(importable_names, args.walk))

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
        for path in sorted(to_evaluate):
            file_specific_args = [path]
            modulename = to_evaluate[path]
            if modulename:
                file_specific_args.append('--modulename={}'.format(modulename))
            # use Popen to capture STDOUT and print it so that regression
            # test may redirect sys.stdout to evaluate it
            p = Popen(sub_args + file_specific_args, stdin=PIPE, stdout=PIPE,
                      stderr=STDOUT, universal_newlines=True)
            stdout, _stderr = p.communicate()
            print(stdout, end='')

            if p.returncode != Script.OK_STATUS:
                exitcode = p.returncode
                if p.returncode != Script.MISMATCH_STATUS:
                    break

    return exitcode


if __name__ == '__main__':

    sys.exit(main())
