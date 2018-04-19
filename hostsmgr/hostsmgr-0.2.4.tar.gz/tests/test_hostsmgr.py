#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `hostsmgr` package."""

import pytest
import os.path
import tempfile
from hostsmgr import HostsMgr
from hostsmgr.hostsmgr import guess_hosts_path
from hostsmgr.entries import HostsEntry, CommentEntry, RawEntry
from hostsmgr.conditions import IPAddress, Host


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
    required_hosts = '127.0.0.1\tabc.com\n'
    assert dst_hosts == required_hosts


def test_access_through_file(mgr):
    path = os.path.join(os.path.dirname(__file__), 'data/hosts.txt')
    mgr.load(path)

    # Save as string
    mgr.saves()

    # Save to temp file
    afile = tempfile.TemporaryFile(mode='w')
    with afile:
        mgr.save(afile)

    assert mgr.check(IPAddress('127.0.0.1'))
    assert mgr.check(IPAddress('127.0.1.1'))
    assert mgr.check(IPAddress('::1'))
    assert mgr.check(IPAddress('fe00::0'))
    assert mgr.check(IPAddress('ff00::0'))
    assert mgr.check(IPAddress('ff02::1'))
    assert mgr.check(IPAddress('ff02::2'))
    assert mgr.check(Host('localhost'))
    assert mgr.check(Host('myhostname'))
    assert mgr.check(Host('ip6-localhost'))
    assert mgr.check(Host('ip6-loopback'))
    assert mgr.check(Host('ip6-localnet'))
    assert mgr.check(Host('ip6-mcastprefix'))
    assert mgr.check(Host('ip6-allnodes'))
    assert mgr.check(Host('ip6-allrouters'))
    assert mgr.check(IPAddress('127.0.0.1') & Host('localhost'))
    assert mgr.check(IPAddress('127.0.1.1') & Host('myhostname'))
    assert not mgr.check(IPAddress('127.0.0.1') & Host(
        'localhost') & Host('myhostname'))
    assert not mgr.check(IPAddress('127.0.0.1') & Host(
        'localhost') & Host('ip6-localhost'))
