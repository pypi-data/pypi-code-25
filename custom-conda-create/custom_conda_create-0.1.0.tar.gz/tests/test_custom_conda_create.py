#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `custom_conda_create` package."""


import unittest
from click.testing import CliRunner

from custom_conda_create import custom_conda_create
from custom_conda_create import cli
from custom_conda_create.util import shell_funcs
from custom_conda_create.util import click_funcs


class TestCustom_conda_create(unittest.TestCase):
    """Tests for `custom_conda_create` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        # runner = CliRunner()
        # result = runner.invoke(cli.main)
        # assert result.exit_code == 0
        # assert 'custom_conda_create.cli.main' in result.output
        # help_result = runner.invoke(cli.main, ['--help'])
        # assert help_result.exit_code == 0
        # assert '--help  Show this message and exit.' in help_result.output
