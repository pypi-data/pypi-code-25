from __future__ import absolute_import
from __future__ import print_function

import unittest
import xtt

from pyasn1.codec.der.decoder import decode as der_decode
from pyasn1_modules import rfc5208, rfc5280


class TestASN1(unittest.TestCase):

    def test_x509_from_ed25519_key_pair(self):
        pub = xtt.ED25519PublicKey(
            b"""^\x970Y=\\\x92\xbdsK2\x0cD%\x96\xf8\x1dh\xc4\x1d&k'+\x1a\xca\xd6\x16\x12\x90\x03="""
        )
        priv = xtt.ED25519PrivateKey(
            b"""\xd1%\xce\xec\xfb\xdf\x82\xb1w~\xb5AL*\x10'\x9aX\x8f\xae\x05\tTm5\xafC\x14\x06]\xb3X^\x970Y=\\\x92\xbdsK2\x0cD%\x96\xf8\x1dh\xc4\x1d&k'+\x1a\xca\xd6\x16\x12\x90\x03="""
        )
        common_name = xtt.Identity(b'\xfd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        cert = xtt.x509_from_ed25519_key_pair(pub, priv, common_name)

        decoded = der_decode(cert, asn1Spec=rfc5280.Certificate(), decodeOpenTypes=True)[0]
        decoded_common_name = decoded['tbsCertificate']['subject'][0][0][0]['value']['utf8String']
        self.assertEqual(decoded_common_name, "FD000000000000000000000000000000")

    def test_asn1_from_ed25519_private_key(self):
        priv = xtt.ED25519PrivateKey(
            b"""\xd1%\xce\xec\xfb\xdf\x82\xb1w~\xb5AL*\x10'\x9aX\x8f\xae\x05\tTm5\xafC\x14\x06]\xb3X^\x970Y=\\\x92\xbdsK2\x0cD%\x96\xf8\x1dh\xc4\x1d&k'+\x1a\xca\xd6\x16\x12\x90\x03="""
        )
        asn1 = xtt.asn1_from_ed25519_private_key(priv)

        decoded = der_decode(asn1, asn1Spec=rfc5208.PrivateKeyInfo(), decodeOpenTypes=True)[0]
        decoded_private_key = der_decode(decoded['privateKey'])[0].asOctets() # privateKey is itself another octet string
        self.assertEqual(decoded_private_key, priv.data[:32])
