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

from ._script import showpath


class DocString(object):

    """Perform docstring comparison and update for a single decorator usage.

    :param Script script:
        script containing docstring decorator

    :param int linenum:
        decorator call location (the last line)

    :param str source_docstr:
        docstring of the class, method, or function that the decorated
        class, method, or function's docstring was copied from or based on

    :param str copied_docstr:
        docstring of the decorated class, method, or function that was
        copied from the source (or in the case of the @based_on, the copied
        docstring provided as the second argument to the decorator)

    :param str changed_docstr:
        the docstring of the decorated class, method, or function that is
        a modified copy of the source docstring (applicable only for the
        @based_on decorator)

    :param bool basis:
        indication if ``copied_docstr`` a result of @based_on usage
        (when ``false``, was a result of @copied_from usage)

    """

    def __init__(self, script, linenum, source_docstr, copied_docstr,
                 changed_docstr=None, basis=False):
        self.script = script
        self.linenum = linenum
        self.source_docstr = source_docstr
        self.copied_docstr = copied_docstr
        self.changed_docstr = changed_docstr
        self.basis = basis

        # caches
        self._clean_copied_docstr = None
        self._clean_source_docstr = None
        self._clean_changed_docstr = None

    @property
    def mismatch(self):
        """Indication if docstring update is needed.

        In the case of @copied_from, compare source docstring against
        docstring of decorated class, function, or method. In the case
        of @based_on, compare source docstring against the copied value
        provided as the second argument to @based_on.

        :returns: indication if docstring update needed
        :rtype: bool

        """
        # try easy comparison first
        match = self.source_docstr == self.copied_docstr

        if not match:
            # compare docstrings with their leading whitespace stripped
            match = self.clean_source_docstr == self.clean_copied_docstr

        return not match

    @property
    def clean_source_docstr(self):
        """Return source docstring with leading whitespace stripped.

        Return normalized docstring of the class, method, or function that
        the decorated class, method, or function's docstring was copied
        from or based on.

        :returns; docstring
        :rtype: str

        """
        if self._clean_source_docstr is None:
            self._clean_source_docstr = self.strip_indent(self.source_docstr)
        return self._clean_source_docstr

    @property
    def clean_copied_docstr(self):
        """Return source docstring with leading whitespace stripped.

        Return normalized docstring of the decorated class, method, or
        function that was copied from the source (or in the case of the
        @based_on, the copied docstring provided as the second argument
        to the decorator).

        :returns; docstring
        :rtype: str

        """
        if self._clean_copied_docstr is None:
            self._clean_copied_docstr = self.strip_indent(self.copied_docstr)
        return self._clean_copied_docstr

    @property
    def clean_changed_docstr(self):
        """Return source docstring with leading whitespace stripped.

        Return normalized docstring of the decorated class, method, or
        function that is a modified copy of the source docstring (applicable
        only for the @based_on decorator)

        :returns; docstring
        :rtype: str

        """
        if self._clean_changed_docstr is None:
            self._clean_changed_docstr = self.strip_indent(self.changed_docstr)
        return self._clean_changed_docstr

    @staticmethod
    def strip_indent(docstr):
        """Remove common leading indentation from docstring.

        Determine indentation level of line with least amount of leading
        whitespace (of the lines with non-whitespace characters). Dedent
        all docstring lines by that amount.

        :returns: normalized docstring
        :rtype: str

        """
        if '\n' in docstr:
            lines = docstr.split('\n')

            indents = []
            for line in lines[1:]:
                unindented_line = line.lstrip()
                if unindented_line:
                    indents.append(len(line) - len(unindented_line))

            if indents:
                indent = min(indents)
            else:
                indent = 0

            lines[1:] = [line[indent:] for line in lines[1:]]

            docstr = '\n'.join(lines)

        return docstr
    
    def get_mismatch_error(self):
        """Get error description for docstring which requires update.

        :returns: error description
        :rtype: str

        """
        if self.changed_docstr is None:
            linenum = self.linenum
            desc = 'docstring update required'
        else:
            linenum = self.linenum
            desc = 'docstring merge required'

        return '{}:{}: {}'.format(showpath(self.script.path), linenum, desc)

    def merge(self, threeway):
        """Update docstring in script.

        Update script source code with new copy of docstring based on
        the source docstring value.

        :param bool threeway:
            update via a three way merge (a @based_on update is present)
        """

        if self.changed_docstr is None:

            # update copied docstring
            self.script.replace_docstr_lines(
                self.script.left_lines, self.linenum, self.clean_source_docstr,
                above=self.basis)

            if threeway:
                # update copied docstring in all script copies involved

                self.script.replace_docstr_lines(
                    self.script.basis_lines, self.linenum,
                    self.clean_source_docstr, above=self.basis)

                self.script.replace_docstr_lines(
                    self.script.right_lines, self.linenum,
                    self.clean_source_docstr, above=self.basis)

        else:
            # updated docstring of class/function/method decorated via @based_on

            self.script.replace_docstr_lines(
                self.script.basis_lines, self.linenum, self.clean_copied_docstr)

            self.script.replace_docstr_lines(
                self.script.left_lines, self.linenum, self.clean_source_docstr)

            self.script.replace_docstr_lines(
                self.script.right_lines, self.linenum, self.clean_changed_docstr)
