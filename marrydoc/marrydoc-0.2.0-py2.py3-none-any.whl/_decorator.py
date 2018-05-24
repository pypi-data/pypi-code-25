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

import inspect
import os
from fnmatch import fnmatch

from ._docstring import DocString
from ._script import Mode, Script


def get_origin(level=2):
    """Determine script path and line number of decorator usage.

    :param int level:
        frame index where decorator usage occurred (relative from the
        current frame in which this function executes)

    :returns:
        absolute path and line number
    :rtype: str, int
    """
    frame = inspect.getouterframes(inspect.currentframe())[level]
    path = os.path.abspath(frame[1])
    return path, frame[2]  # linenum


def pass_through(func_or_class):
    """Pass object through untouched (to be used as decorator).

    :param func_or_class:
        decorated class, function, or method
    :type func_or_class: type or function or classmethod or staticmethod

    :returns:
        untouched object
    :rtype: type or function or classmethod or staticmethod

    """
    return func_or_class


def resolve_method_wrapper(func_or_class):
    """Resolve static/class method wrapper.

    :param func_or_class:
        decorated class, function, or method
    :type func_or_class: type or function or classmethod or staticmethod

    :returns:
        true docstring owner
    :rtype: type or function

    """
    try:
        # return method within static and class method wrappers
        owner = func_or_class.__func__
    except AttributeError:
        # must have been normal class, function or method, just return it
        owner = func_or_class

    return owner


def get_docstring(source, owner=None):
    """Get docstring from original source.

    :param source:
        source of docstring as pointed to by marrydoc decorator
    :type source: str or function or type

    :param owner:
        decorated class, function or method (or ``None`` if from ``@based_on``)
    :type owner: type or function

    :returns:

    :rtype: str

    """
    if owner is None or isinstance(owner, type):
        # due to @based_on usage or class was decorated
        if isinstance(source, str):
            # marrydoc decorator was pointed to docstring itself
            source_docstr = source
        else:
            # marrydoc decorator was pointed to a class or function
            source_docstr = source.__doc__
    else:
        # marrydoc decorator was used by a function/method
        if isinstance(source, str):
            # marrydoc decorator was pointed to docstring itself
            source_docstr = source
        elif isinstance(source, type):
            # marrydoc decorator was pointed to a class, get docstring from
            # method by same name
            source_docstr = getattr(source, owner.__name__).__doc__
        else:
            # marrydoc decorator was pointed to a function/method
            source_docstr = source.__doc__

    return source_docstr


class InheritDecorator(object):

    """Decorator for copying docstrings."""

    def __init__(self, source):
        self.source = source

    def __call__(self, func_or_class):

        docstr_owner = resolve_method_wrapper(func_or_class)

        source_docstr = get_docstring(self.source, docstr_owner)

        docstr = docstr_owner.__doc__
        assert docstr is None, 'docstring already present, @inherit blocked'

        docstr_owner.__doc__ = source_docstr

        return func_or_class


def inherit(source):
    """Provide decorator to copy docstring from source into decorated object.

    Return decorator that copies docstring from the ``source`` (or the
    source itself it is an ``str``) into the docstring of the decorated
    class, function, classmethod, or static method.

    :param source:
        string value, class, method, or function for decorated function to
        inherit docstring from
        class, method, or function containing the doctring to copy into the
        decorated class, method, or function's docstring (or the source
        docstring value itself)
    :type source: str or type or function or classmethod or staticmethod

    :returns: decorator
    :rtype: function

    """
    return InheritDecorator(source)


class CopiedFromDecorator(InheritDecorator):

    """Decorator for verifying/updating copied docstrings."""

    def __call__(self, func_or_class):
        path, linenum = get_origin()

        if fnmatch(path, Script.path_of_interest):

            docstr_owner = resolve_method_wrapper(func_or_class)

            source_docstr = get_docstring(self.source, docstr_owner)

            script = Script.get_instance(path)

            docstrings = DocString(
                script, linenum, source_docstr, docstr_owner.__doc__)

            if docstrings.mismatch:
                script.add_mismatch(docstrings)

        return func_or_class


def copied_from(source):
    """Provide decorator to verify and update copied docstring.

    Return decorator that facilitates the evaluation and update of
    a class, function, or method docstring that was copied from another
    code docstring.

    :param source:
        class, method, or function containing the doctring that the
        decorated class, method, or function's docstring was copied from
        (or the source docstring value itself)
    :type source: str or type or function or classmethod or staticmethod

    :returns: decorator
    :rtype: function

    """
    if Script.mode is Mode.IGNORE:
        decorator = pass_through
    else:
        decorator = CopiedFromDecorator(source)
    return decorator


class BasedOnDecorator(InheritDecorator):

    """Decorator for verifying/updating docstrings that are modified copies."""

    def __init__(self, source, docstr, path, linenum):
        # source, docstr -> see @based_on decorator
        # path, linenum -> script location of @based_on this instance is for
        self._based_on_docstr = docstr
        self._path = path
        self._linenum = linenum
        self._source_docstr = None
        self._source_mismatch = False

        super(BasedOnDecorator, self).__init__(source)

    def __call__(self, func_or_class):
        path, linenum = get_origin()

        if path != self._path:
            raise RuntimeError(
                "Application of based_on() decorator must be within the "
                "same script the decorator was created.")

        script = Script.get_instance(path)

        docstr_owner = resolve_method_wrapper(func_or_class)

        source_docstr = get_docstring(self.source, docstr_owner)

        if self._source_docstr is None:
            # first use - evaluate if source docstring has changed (if so
            # then the "docstr" in @based_on decorator needs update)

            self._source_docstr = source_docstr

            docstring = DocString(
                script, self._linenum, source_docstr, self._based_on_docstr,
                basis=True)

            self._source_mismatch = docstring.mismatch

            if self._source_mismatch:
                script.add_mismatch(docstring)

        elif source_docstr != self._source_docstr:
            # when "source" is a class, block the decorator from being used
            # to decorate two different methods
            raise RuntimeError(
                "Separate based_on() decorators must be used for each "
                "unique source method docstring.")

        if self._source_mismatch:
            # force a merge of the decorated class/function/method's
            # docstring since source docstring changed
            docstring = DocString(
                script, linenum, source_docstr, self._based_on_docstr,
                changed_docstr=docstr_owner.__doc__)
            script.add_mismatch(docstring)

        return func_or_class


def based_on(source, docstr):
    """Provide decorator to verify and update a modified copy of a docstring.

    Return decorator that facilitates the evaluation and update of
    a class, function, or method docstring that is a modified copied of
    another code docstring.

    :param source:
        class, method, or function containing the doctring that the
        decorated class, method, or function's docstring is based on
        (or the source docstring value itself)
    :type source: str or type or function or classmethod or staticmethod

    :param str docstr:
        a copy of the ``source`` docstring (used to detect if the ``source``
        docstring has changed and if it has to perform the three way merge to
        update the docstring of the decorated class, method, or function.

    :returns: decorator
    :rtype: function

    """
    path, linenum = get_origin()

    if Script.mode is Mode.IGNORE or not fnmatch(path, Script.path_of_interest):
        decorator = pass_through
    else:
        decorator = BasedOnDecorator(source, docstr, path, linenum)

    return decorator
