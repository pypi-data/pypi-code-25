#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from subprocess import check_call
from shlex import split as parse_command

import pytest

with open("Makefile", "r") as f:
    for line in f.readlines():
        if line[0:6] == "python":
            python_command = line.split(" = ")[-1]

base_command = "%s examples/" % python_command

def assert_exec(f):
    ret_code = check_call(
        parse_command("%s%s" % (base_command, f))
    )
    assert ret_code == 0

def test_basic_api_call():
    assert_exec("basic_api_call.py")

def test_basic_sync_scraper():
    assert_exec("basic_sync_scraper.py")

@pytest.mark.end2end
def test_basic_async_scraper():
    assert_exec("basic_async_scraper.py")

@pytest.mark.end2end
def test_fast_async_scraper():
    assert_exec("fast_async_scraper.py")

