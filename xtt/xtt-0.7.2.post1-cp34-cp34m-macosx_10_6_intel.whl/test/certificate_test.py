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

import datetime
import unittest

import xtt

class TestCertificates(unittest.TestCase):

    def test_generate_ed25519_server_certificate(self):
        expiry = xtt.CertificateExpiry(b'21001231')
        root_id = xtt.CertificateRootId(b'0000111100001111')
        server_id = xtt.Identity(b'0000222200002222')
        (root_pub, root_priv) = xtt.create_ed25519_key_pair()
        (server_pub, server_priv) = xtt.create_ed25519_key_pair()

        cert = xtt.generate_ed25519_server_certificate (server_id,
                                                        server_pub,
                                                        expiry,
                                                        root_id,
                                                        root_priv)
        self.assertTrue(b'21001231' in cert.data)

class TestCertificateExpiry(unittest.TestCase):

    def test_datetime_prop(self):
        expiry = xtt.CertificateExpiry(b'19850704')
        self.assertEqual(expiry.datetime, datetime.datetime(1985, 7, 4))

    def test_from_datetime(self):
        dt = datetime.datetime(1985, 7, 4)
        expiry = xtt.CertificateExpiry.from_datetime(dt)
        self.assertEqual(expiry.data, b'19850704')

class TestED25519ServerCertificate(unittest.TestCase):

    def setUp(self):
        self.expiry = xtt.CertificateExpiry(b'21001231')
        self.root_id = xtt.CertificateRootId(b'0000111100001111')
        self.server_id = xtt.Identity(b'0000222200002222')
        (self.root_pub, self.root_priv) = xtt.create_ed25519_key_pair()
        (self.server_pub, self.server_priv) = xtt.create_ed25519_key_pair()

        self.cert = xtt.generate_ed25519_server_certificate (self.server_id,
                                                             self.server_pub,
                                                             self.expiry,
                                                             self.root_id,
                                                             self.root_priv)

    def test_id(self):
        id = self.cert.id
        self.assertEqual(id.data, b'0000222200002222')

    def test_expiry(self):
        expiry = self.cert.expiry
        self.assertEqual(expiry.data, b'21001231')

    def test_root_id(self):
        root_id = self.cert.root_id
        self.assertEqual(root_id.data, b'0000111100001111')

    def test_public_key(self):
        public_key = self.cert.public_key
        self.assertEqual(public_key.data, self.server_pub.data)
