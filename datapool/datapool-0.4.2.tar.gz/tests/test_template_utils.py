# encoding: utf-8
from __future__ import print_function, division, absolute_import

from datapool.templates.utils import template_variables, ask_values


def test_template_variables():

    t = """{a}
    abd {b_x}
    {c_}"""
    assert template_variables(t) == ["a", "b_x", "c_"]


def test_ask_values_complete(regtest):

    def mock_input(message):
        field = message.split(" ", 1)[0]
        return field + "x"

    presets = {}
    names = ('city', 'description', 'name', 'postcode', 'street', 'x', 'y', 'z')
    for _ in ask_values(names, presets, input_=mock_input):
        pass
    print(sorted(presets.items()), file=regtest)


def test_ask_values_aborted(regtest):

    def mock_input(message):
        field = message.split(" ", 1)[0]
        if field == "x":
            return "."
        return field + "x"

    presets = {}
    names = ('city', 'description', 'name', 'postcode', 'street', 'x', 'y', 'z')
    for result in ask_values(names, presets, input_=mock_input):
        if result is None:
            break
    print(sorted(presets.items()), file=regtest)
