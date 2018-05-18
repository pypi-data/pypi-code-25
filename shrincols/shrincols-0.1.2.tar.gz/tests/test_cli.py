import pytest

from shrincols import cli

default_size      = '40'
fake_file         = 'lalala.txt'
input_file        = 'tests/input.txt'
output_normal     = 'tests/output_normal.txt'
output_justified  = 'tests/output_justified.txt'
samples_normal    = {
    "hi there my name is bot, would you like to have a coffee":
    """hi there my name is bot,
would you like to have a
coffee""",
    "hi there again, we are making some tests here, have you ever seen the rain?":
    """hi there again, we are
making some tests here,
have you ever seen the
rain?"""
}
samples_justified = {
    "hello my friend, i am not that cool":
    "hello  my  friend,  i  am  not that cool",
    "but i am always trying to be":
    "but   i   am   always   trying   to   be"
}

@pytest.fixture()
def parser():
    return cli.create_parser()

def test_parser_without_arguments(parser):
    """
    If no arguments are given, must exit
    """
    with pytest.raises(SystemExit):
        parser.parse_args([])

def test_parser_without_input(parser):
    """
    Without a input string or filename, must cause error
    """
    with pytest.raises(SystemExit):
        parser.parse_args(['-c', default_size])

def test_if_file_does_not_exists(parser):
    """
    If the input is a filename, the file must exist
    """
    with  pytest.raises(SystemExit):
        parser.parse_args([fake_file, '-c', default_size])

def test_if_file_exist(parser):
    """
    If the file exists, must continue
    """
    args = parser.parse_args([input_file, '-c', default_size])
    assert args.filename

def test_if_input_is_string(parser):
    """
    If the input is a string, them it must continue
    """
    with open(input_file, 'r') as f:
        text = f.read()
        args = parser.parse_args([text, '-c', default_size])
        assert args.string

def test_max_cols_not_integer(parser):
    """
    If the --col argument is not a number, must fail
    """
    with  pytest.raises(SystemExit):
        parser.parse_args([input_file, '-c', 'aaa'])

def test_full_text_with_justify(parser):
    """
    check if input and output as in files match using justify option
    """
    args = parser.parse_args([input_file, '-c', default_size, '-j'])
    result = cli.manager(args)
    with open(output_justified, 'r') as f:
        assert result == f.read()

def test_full_text(parser):
    """
    check if input and output as in files match
    """
    args = parser.parse_args([input_file, '-c', default_size])
    result = cli.manager(args)
    with open(output_normal, 'r') as f:
        assert result == f.read()

def test_shrink_cols(parser):
    """
    check whether some simple string get shrinked
    """
    cols = 25
    for k, v in samples_normal.items():
        assert cli.shrink_cols(k, cols) == v

def test_justify(parser):
    """
    check whether the justify function is working properly
    """
    cols = int(default_size)
    for k, v in samples_justified.items():
        assert cli.justify(k, cols) == v
    
