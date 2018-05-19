""" Terms tree source parsing code

Expected format is 'tab tree' :

item 0
    item 0 0 [key1=value1 "key 2"="value 2"]
    item 0 1
        item 0 1 0
item 1 [key=value]
"""

import re

from .node import Node
from .utils import parse_kv_pairs


class SyntaxError(Exception):
    pass


def loads(source):
    """

    :param str source: string with terms tree
    :return: terms tree (root node)
    """
    assert isinstance(source, str)
    return _parse(_tokens(source.splitlines()))


def load(file_obj):
    """

    :param file_obj: file object with terms tree source
    :return:
    """
    assert hasattr(file_obj, 'read'), 'File object argument required'
    return _parse(_tokens(file_obj))


# regexp for valid terms tree line: <prefix> <term> <data> <optional comment>
_LINE_REGEXP = re.compile('^(?P<prefix>\s*)(?P<term>[^\[\]]*?)\s*(?:\[(?P<data>.*)\])?\s*(?:\#.*)?$')


def _tokens(lines):
    """ Yield parsed line as tuple (line_n, indentation_level, term_string, data_string)"""
    prefix_char = None
    prefix_step = None  # chars number in single indentation

    for line_n, line in enumerate(lines, 1):

        match = _LINE_REGEXP.match(line)
        if not match:
            raise SyntaxError('wrong line %d format' % line_n)
        prefix, term, data = match.groups()
        if not term:
            continue

        if prefix:
            # check prefix contains only single char
            if prefix[0] * len(prefix) != prefix:
                raise SyntaxError('mix of tabs and spaces in line %d' % line_n)
            # check prefix is from same chars as prev
            if prefix_char and prefix_char != prefix[0]:
                raise SyntaxError('indetation char in line %d differs from previous lines prefix char' % line_n)
            # fill prefix info if first indentation
            if prefix_char is None:
                prefix_char = prefix[0]
                prefix_step = len(prefix)
            # check indentation size is correct
            indentation_level, remainder = divmod(len(prefix), prefix_step)
            if remainder:
                raise SyntaxError('line %d indentation size error' % line_n)
        else:
            indentation_level = 0

        yield (line_n, indentation_level, term, data)


def _parse(tokens):
    """

    :param tokens: results yielded by _tokens function
    :return: terms tree as list of first level nodes
    """
    parent = root = Node(None)
    node = None
    prev_level = 0

    for line_n, level, term, data_str in tokens:
        if level > prev_level:  # indent
            if level != prev_level + 1 or node is None:
                raise Exception('line %d indentation level error' % line_n)
            parent = node
        else:  # unindent
            for _ in range(prev_level-level):
                parent = parent.parent
        try:
            data = parse_kv_pairs(data_str) or None
        except ValueError:
            raise SyntaxError('invalid data string format in line %d' % line_n)
        node = Node(term, data)
        node.parent = parent
        parent.children.append(node)
        prev_level = level
    return root
