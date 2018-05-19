from io import StringIO

import pytest

from termstree.parser import (
    loads,
    load,
    _tokens,
    SyntaxError
)


def test_tokenizer():
    src = """

# comment

# comment for item 0
item 0[data]  
  item 0 0 # comment
  item 0 1
    item 0 1 0 
    item 0 1 1
  item 0 1 [data] # comment

item 1
"""
    assert [
               # line_n, indentation level, term, data str
               (6, 0, 'item 0', 'data'),
               (7, 1, 'item 0 0', None),
               (8, 1, 'item 0 1', None),
               (9, 2, 'item 0 1 0', None),
               (10, 2, 'item 0 1 1', None),
               (11, 1, 'item 0 1', 'data'),
               (13, 0, 'item 1', None),
           ] == list(_tokens(src.splitlines()))


def test_tokenizer_src_with_all_lines_indeted():
    s = "\tA\n\t\tB\n\tC"  # all lines has offset '\t'
    assert [
               (1, 1, 'A', None),
               (2, 2, 'B', None),
               (3, 1, 'C', None),

           ] == list(_tokens(s.splitlines()))


def test_tokenizer_error_different_space_symbols_in_prefix():
    s = "A\n\t  B"
    with pytest.raises(SyntaxError):
        list(_tokens(s.splitlines()))


def test_tokenizer_error_different_prefixes():
    s = "A\n\tB\n  C"
    with pytest.raises(SyntaxError):
        list(_tokens(s.splitlines()))


def test_tokenizer_error_wrong_tail():
    s = "A\n\tB [data] oops"
    with pytest.raises(SyntaxError):
        list(_tokens(s.splitlines()))


def test_tokenizer_error_wrong_indentation_size():
    s = "A\n  B\n C"  # step is two spaces (first line), next line - one space
    with pytest.raises(SyntaxError) as ex:
        list(_tokens(s.splitlines()))
    assert 'indentation size error' in str(ex)


def test_empty_content_parsing():
    tree = loads('')
    assert [] == tree.children
    assert None == tree.term


def test_base_case():
    src = """
A
    B
        # comment 1 for C

        C # comment 2 for C
        D
# comment for E
E [key1=value1 "key 2"="value 2" ]
    """
    root = loads(src)
    assert 'A' == root[0].term

    assert 'B' == root[0][0].term
    assert 'B' == root[0, 0].term

    assert 'C' == root[0, 0, 0].term

    assert 'D' == root[0, 0, 1].term
    assert 'D' == root[0, 0, 1].term

    assert 'E' == root[1].term
    assert {'key1': 'value1', 'key 2': 'value 2'} == root[1].data


def test_parse_src_with_invalid_data():
    s = 'A [key1 = value1]'  # space before or after = is not allowed
    with pytest.raises(SyntaxError) as ex:
        loads(s)
    assert 'invalid data string format' in str(ex)


def test_load_from_file():
    root = load(StringIO('A[k=v]\n\tB\n\tC'))
    assert {'k': 'v'} == root[0].data
    assert 'B' == root[0, 0].term
