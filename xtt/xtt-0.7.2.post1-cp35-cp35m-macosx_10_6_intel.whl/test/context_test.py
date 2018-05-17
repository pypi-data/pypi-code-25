# Copyright 2018 Xaptum, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License

from __future__ import absolute_import
from __future__ import print_function

import six
import unittest
import xtt

class TestIORequest(unittest.TestCase):
    pass

class TestServerHandshakeContext(unittest.TestCase):

    def test_init_succeeds(self):
        ctx = xtt.ServerHandshakeContext()

    def test_handle_connect_returns_want_read(self):
        ctx = xtt.ServerHandshakeContext()
        with self.assertRaises(xtt.XTTWantReadError):
            ctx.handle_connect()
        self.assertGreater(len(ctx.io_buffer), 0)

class TestClientHandshakeContext(unittest.TestCase):

    def test_init_succeeds(self):
        version = xtt.Version.ONE
        suite_spec = xtt.SuiteSpec.XTT_X25519_LRSW_ED25519_CHACHA20POLY1305_SHA512
        ctx = xtt.ClientHandshakeContext(version, suite_spec)

    def test_init_fails_on_unknown_version(self):
        version = 100
        suite_spec = xtt.SuiteSpec.XTT_X25519_LRSW_ED25519_CHACHA20POLY1305_SHA512
        with self.assertRaisesRegex(xtt.XTTError, 'UNKNOWN_VERSION'):
            ctx = xtt.ClientHandshakeContext(version, suite_spec)

    def test_init_fails_on_unknown_suite_spec(self):
        version = xtt.Version.ONE
        suite_spec = 100
        with self.assertRaisesRegex(xtt.XTTError, "UNKNOWN_CRYPTO_SPEC"):
            ctx = xtt.ClientHandshakeContext(version, suite_spec)

class TestServerCookieContext(unittest.TestCase):

    def test_init_succeeds(self):
        ctx = xtt.ServerCookieContext()

class TestServerED25519CertificateContext(unittest.TestCase):
    pass

class TestClientLRSWGroupContext(unittest.TestCase):

    def test_init_succeeds(self):
        gid = xtt.GroupId()
        priv_key = xtt.LRSWPrivateKey()
        credential = xtt.LRSWCredential()
        basename = b'BASENAME'
        ctx = xtt.ClientLRSWGroupContext(gid, priv_key, credential, basename)
