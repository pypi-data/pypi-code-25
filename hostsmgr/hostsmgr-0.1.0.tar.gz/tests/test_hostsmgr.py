#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `hostsmgr` package."""

import io
import pytest

from hostsmgr import HostsMgr
from hostsmgr.hostsmgr import guess_hosts_path
from hostsmgr.entry import *


@pytest.fixture
def mgr():
    """Default hosts manager fixture
    """

    amgr = HostsMgr()
    return amgr


def test_clear(mgr):
    """Test if clear function works
    """

    mgr.loads("  # Test sample\n127.0.0.1 localhost\n")
    assert len(mgr._entries) == 2

    mgr.clear()
    assert len(mgr._entries) == 0


def test_guess_hosts_path():
    guess_hosts_path()


def test_load_entries_from_string(mgr):

    mgr.loads("")
    assert len(mgr._entries) == 0

    mgr.loads("127.0.0.1 localhost")
    assert (len(mgr._entries) == 1) and (
        isinstance(mgr._entries[0], HostsEntry))

    mgr.loads("127.0.0.1 localhost\n")
    assert (len(mgr._entries) == 1) and (
        isinstance(mgr._entries[0], HostsEntry))

    mgr.loads("127.0.0.1")
    assert (len(mgr._entries) == 1) and (isinstance(mgr._entries[0], RawEntry))

    mgr.loads("#")
    assert (len(mgr._entries) == 1) and (
        isinstance(mgr._entries[0], CommentEntry))

    mgr.loads("# ")
    assert (len(mgr._entries) == 1) and (
        isinstance(mgr._entries[0], CommentEntry))

    mgr.loads(" # ")
    assert (len(mgr._entries) == 1) and (
        isinstance(mgr._entries[0], CommentEntry))

    mgr.loads("    # ")
    assert (len(mgr._entries) == 1) and (
        isinstance(mgr._entries[0], CommentEntry))

    mgr.loads(" # \n\n")
    assert (len(mgr._entries) == 2) and (
        isinstance(mgr._entries[0], CommentEntry))

    mgr.loads(" # hello!\n\n#kknd")
    assert (len(mgr._entries) == 3) and (
        isinstance(mgr._entries[0], CommentEntry)) and (
        isinstance(mgr._entries[2], CommentEntry))


def test_save_entries_to_string(mgr):
    src_hosts = "127.0.0.1     abc.com"
    mgr.loads(src_hosts)
    dst_hosts = mgr.saves()
    required_hosts = '127.0.0.1\tabc.com'
    assert dst_hosts == required_hosts
