#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `marmee.model` package."""

import pytest
from marshmallow import fields, post_load
from marmee.model.input import (
    Input,
    InputSchema,
    ArgumentSchema
)
from marshmallow import pprint


class TestInput(object):
    """docstring for testing marmee.model.input ."""

    @pytest.fixture
    def input(self):

        class ArgumentSchemaInstance(ArgumentSchema):
            
            def __init__(self, positional, identifier, values):
                self.positional = positional
                self.identifier = identifier
                self.values = values

            @post_load
            def make_argument(self, data):
                return Argument(**data)

        # first_arg = ArgumentSchemaInstance().load(
        #     positional=self.positional,
        #     identifier=self.identifier,
        #     values=self.values #  fields.List.load(["first","second"])
        # )
        first_arg = ArgumentSchemaInstance(
            False,
            "first",
            ["first","second"]
        )
        second_arg = ArgumentSchemaInstance(
            False,
            "second",
            ["first","second"]
        )

        pprint(first_arg)

        return InputSchema().load(
            process="firttest",
            arguments={
                first_arg,
                second_arg
            }
        )


    def test_mandatory(self):
        print(self)
        try:
            assert self.input().process
            # assert self.process
            # assert self.arguments
        except Exception as e:
            raise
