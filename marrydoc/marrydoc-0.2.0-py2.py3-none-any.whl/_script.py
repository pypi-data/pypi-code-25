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

from __future__ import absolute_import, division, print_function, unicode_literals

import difflib
import os
import re
import subprocess
from enum import Enum
from subprocess import PIPE


# list of tuples:
#    (subprocess command arguments to check for tool's existence,
#     template of three way merge command (same format as env variable setting)
MERGE_COMMAND_CANDIDATES = [
    (['kdiff3', '-v'],
     'kdiff3 --merge --auto {base} {left} {right} --output {orig}'
     ),
]


def showpath(path):
    """Get path to show user.

    :returns: path relative to current working directory
    :rtype: str

    """
    relpath = os.path.relpath(path, os.getcwd())

    if not relpath.startswith('..'):
        path = relpath

    return path


class Mode(Enum):

    """MarryDoc mode of operation."""

    IGNORE = 0
    """Ignore docstring inconsistencies."""

    CHECK = 1
    """Print needed updates to married docstrings."""

    MERGE = 2
    """Merge changes in source docstrings into married docstrings."""


class Script(object):

    """Manage docstring updates in script source file.

    :param str path: script location

    """

    REGEX = re.compile(
        r'(?P<prefix>.*?""")(?P<docstr>.*?)"""(?P<suffix>.*)', re.DOTALL)

    test_mode = False

    instances = {}

    path_of_interest = None  # gets monkey-patched by command line tool

    mode = Mode.IGNORE

    def __init__(self, path):
        self.path = path
        self.original_lines_list = None
        self.basis_lines_list = None
        self.left_lines_list = None
        self.right_lines_list = None
        self.mismatches = []

    def add_mismatch(self, mismatch):
        """Add docstring instance that identifies docstring update needed.

        :param DocString mismatch:
            description of docstring that contains mismatch that needs update

        """
        self.mismatches.append(mismatch)

    @classmethod
    def get_instance(cls, path):
        """Return Script instance associated with given path.

        Provide singletons for every script that is being updated.

        :param str path:
            path of script being updated

        :returns:
            singleton for given path
        :rtype: Script

        """
        try:
            instance = cls.instances[path]
        except KeyError:
            instance = cls(path)
            cls.instances[path] = instance
        return instance

    @property
    def original_lines(self):
        """Return unaltered source file lines.

        :returns:
            script source lines (no newlines)
        :rtype: tuple of str

        """
        if self.original_lines_list is None:
            with open(self.path, 'r') as fh:
                self.original_lines_list = tuple(fh.read().split('\n'))

        return self.original_lines_list

    @property
    def basis_lines(self):
        """Return source file lines to use as a basis for a 3-way merge.

        Returned lines contain updated docstrings (from the docstring
        source) for the class/function/method decorated via @copied_from
        when the source docstring has changed. (These same updates are
        applied to the left and right lines as well in a three way merge.)

        Returned lines contain updated docstrings (from the docstring
        source) for the second parameter of the @based_on decorator
        when the source docstring has changed. (These same updates are
        applied to the left and right lines as well in a three way merge.)

        Returned lines contain updated docstrings (from the value of the
        @based_on second parameter) for the class/function/method decorated
        via @based_on when the source docstring has changed. (The second
        parameter contains the basis from which the source was changed and
        the basis of which the decorated class/function/method docstring was
        modified.)

        :returns:
            script source lines (no newlines)
        :rtype: list of str

        """
        if self.basis_lines_list is None:
            self.basis_lines_list = list(self.original_lines)
        return self.basis_lines_list

    @property
    def left_lines(self):
        """Return updated source file lines containing docstring edits.

        In the case of a three way merge, return the "left" file contents,
        otherwise return the new copy of the source file.

        Returned lines contain updated docstrings (from the docstring
        source) for the class/function/method decorated via @copied_from
        when the source docstring has changed. (These same updates are
        applied to the basis and right lines as well in a three way merge.)

        In the case of a three-way merge, returned lines contain updated
        docstrings (from the docstring source) for the class/function/method
        decorated via @based_on when the source docstring has changed. (The
        left represents changes made to the source docstring from the basis.)

        :returns:
            script source lines (no newlines)
        :rtype: list of str

        """
        if self.left_lines_list is None:
            self.left_lines_list = list(self.original_lines)
        return self.left_lines_list

    @property
    def right_lines(self):
        """Return source file lines to use as the "right" file in a 3-way merge.

        Returned lines contain updated docstrings (from the docstring
        source) for the class/function/method decorated via @copied_from
        when the source docstring has changed. (These same updates are
        applied to the basis and left lines as well in a three way merge.)

        Returned lines contain the original docstrings for the
        class/function/method decorated via @based_on. (The right represents
        changes made in this script from the source docstring basis.)

        :returns:
            script source lines (no newlines)
        :rtype: list of str

        """
        if self.right_lines_list is None:
            self.right_lines_list = list(self.original_lines)
        return self.right_lines_list

    def get_docstr_match(self, lines, linenum):
        """Find first docstring and return match.

        :param lines:
            lines to search (with newlines stripped)
        :type lines: iterable of str

        :param int linenum:
            line number to start search at

        :returns: regular expression match object
        :rtype: SRE_Match

        """
        content = '\n'.join(lines[linenum:])

        match = self.REGEX.match(content)

        if match is None:
            docstr_not_found = (
                '{}:{}: could not find docstring'.format(self.path, linenum))
            raise RuntimeError(docstr_not_found)

        return match

    def replace_docstr_lines(self, lines, linenum, docstr, above=False):
        """Replace docstring at specific location.

        :param lines:
            lines to search (with newlines stripped)
        :type lines: iterable of str

        :param int linenum:
            line number to start search at

        :param str docstr:
            replacement docstring

        :param bool above:
            search above linenum for first instance (otherwise search below)

        :returns: lines
        :rtype: lines (with newlines stripped)

        """
        if above:
            count = 0
            for index in range(linenum - 1, -1, -1):
                count += lines[index].count('"""')
                if count >= 2:
                    linenum = index
                    break
            else:
                docstr_not_found = (
                    '{}:{}: could not find baseline docstring'.format(self.path, linenum))
                raise RuntimeError(docstr_not_found)

        match = self.get_docstr_match(lines, linenum)

        # determine docstr indent by number of characters before opening triple quote
        # in old docstring
        indent = ' ' * len(match.group('prefix').split('\n')[-1].rstrip('"'))

        # add trailing triple quote early so it gets indented properly
        docstr = docstr + '"""'

        docstr_lines = [
            (indent + x if i and x else x) for (i, x) in enumerate(docstr.split('\n'))]

        new_content = (
                match.group('prefix') + '\n'.join(docstr_lines)) + match.group('suffix')

        lines[linenum:] = new_content.split('\n')

    def get_filename(self, desc):
        """Construct new script filename with special extension.

        :param str desc:
            additional extension text

        :returns:
            script filename
        :rtype: str

        """
        basename, ext = os.path.splitext(self.path)
        return '{}.{}{}'.format(basename, desc, ext)

    def print_diff(self, filename, lines, original_lines=None):
        """Print unified difference summary of changes in lines to console.

        :param str filename:
            file name

        :param lines:
            altered lines(with newlines stripped)
        :type lines: list of str

        :param original_lines:
            unaltered lines (with newlines stripped)
        :type lines: list of str

        """
        linelen = max([len(filename) + 4, 80])
        print('#' * linelen)
        print(' {} '.format(filename).center(linelen, '#'))
        print('#' * linelen)
        if original_lines is None:
            original_lines = self.original_lines
        orig = [line + '\n' for line in original_lines]
        update = [line + '\n' for line in lines]
        print(''.join(difflib.unified_diff(orig, update)), end='')
        print('^' * linelen)

    def write_file(self, path, lines):
        """Write file content to file system.

        :param str path:
            file path

        :param lines:
            file lines (with newlines stripped)

        """
        if self.test_mode:
            print(showpath(path), '... FILE WRITE SUPPRESSED FOR TEST')
        else:
            with open(path, 'w') as fh:
                fh.write('\n'.join(lines))

    _merge_command_template = None

    @property
    def merge_command_template(self):
        """Three way merge command template.

        :returns: template
        :rtype: str
        """
        if Script._merge_command_template is None:
            merge_template = os.environ.get('MARRYDOC_MERGE', '')
            last_candidate_cmd = MERGE_COMMAND_CANDIDATES[-1][0]
            if not merge_template:
                for check_cmd, template in MERGE_COMMAND_CANDIDATES:
                    try:
                        if self.test_mode:
                            # force consistent test coverage no matter test
                            # environment, but exercise as much code as possible
                            exitcode = bool(check_cmd != last_candidate_cmd)
                        else:
                            exitcode = subprocess.call(
                                check_cmd, stdout=PIPE, stderr=PIPE)
                    except OSError:
                        pass
                    else:
                        if exitcode == 0:
                            merge_template = template
                            break
            Script._merge_command_template = merge_template

        return Script._merge_command_template

    def threeway_merge(self, base_filename, left_filename, right_filename):
        """Perform three way merge.

        :param str base_filename:
            basis filename (see ``basis`` property for description of content)

        :param str left_filename:
            left filename (see ``left`` property for description of content)

        :param str right_filename:
            right filename (see ``right`` property for description of content)

        """
        if self.merge_command_template:
            merge_cmd = self.merge_command_template.format(
                left=left_filename, right=right_filename, base=base_filename,
                orig=self.path)
            print(merge_cmd)

            if not self.test_mode and subprocess.call(merge_cmd.split()):

                print(showpath(self.path), '... merge cancelled')
                for path in [base_filename, left_filename, right_filename]:
                    print('{} ... created for manual merge'.format(showpath(path)))
            else:
                print(showpath(self.path), '... UPDATED')

                if not self.test_mode:
                    os.remove(base_filename)
                    os.remove(left_filename)
                    os.remove(right_filename)
        else:
            print(showpath(self.path), '... needs manual three way merge')
            print(MERGE_INSTRUCTIONS.format(MERGE_COMMAND_CANDIDATES[0][1]))

    def merge(self, threeway):
        """Update script.

        If three-way merge selected, create base, left, and right files for
        the merge. If the user configured the environment variable to select
        a merge tool, run it and if successful, remove the three files.

        Otherwise for a normal merge, just update the script.

        :param bool threeway:
            perform three way merge (@based_on update present)

        """
        if threeway:
            base_filename = self.get_filename('base')
            left_filename = self.get_filename('left')
            right_filename = self.get_filename('right')

            if self.test_mode:
                self.print_diff(showpath(base_filename), self.basis_lines_list)

                self.print_diff(
                    showpath(left_filename), self.left_lines_list,
                    self.basis_lines_list)

                self.print_diff(
                    showpath(right_filename), self.right_lines_list,
                    self.basis_lines_list)

            if self.mode is Mode.MERGE:
                self.write_file(base_filename, self.basis_lines_list)
                self.write_file(left_filename, self.left_lines_list)
                self.write_file(right_filename, self.right_lines_list)

                self.threeway_merge(base_filename, left_filename, right_filename)

            else:
                print(showpath(self.path), '... three way merge needed (use --merge)')

        else:
            if self.test_mode:
                self.print_diff(showpath(self.path), self.left_lines_list)

            if self.mode is Mode.MERGE:
                self.write_file(self.path, self.left_lines_list)
                print(showpath(self.path), '... UPDATED')
            else:
                print(showpath(self.path), '... update needed (use --merge)')

    @staticmethod
    def get_linenum(docstring):
        """Get line number where docstring is located.

        :param DocString docstring:
            docstring

        :returns: line number
        :rtype: int

        """
        return docstring.linenum

    def check_for_mismatches(self):
        """Check if script needs update because docstring source has changed.

        Perform merge if selected if needed.

        :returns: indication if script update is needed
        :rtype: bool

        """
        if self.mismatches:
            threeway = any(
                docstring.changed_docstr is not None for docstring in self.mismatches)

            for docstring in sorted(self.mismatches, key=self.get_linenum, reverse=True):
                docstring.merge(threeway)

            self.merge(threeway)
        else:
            print('{} ... OK'.format(showpath(self.path)))

        return Script.MISMATCH_STATUS if self.mismatches else Script.OK_STATUS

    # exit codes
    MISMATCH_STATUS = 99
    OK_STATUS = 0


MERGE_INSTRUCTIONS = """
Set MARRYDOC_MERGE environment variable to perform three way merge with 
tool of your choice. Specify command using Python string formatting. 

For example, on Linux:

  export MARRYDOC_MERGE="{0}"


Or on Microsoft Windows:

  set MARRYDOC_MERGE="{0}"
"""
