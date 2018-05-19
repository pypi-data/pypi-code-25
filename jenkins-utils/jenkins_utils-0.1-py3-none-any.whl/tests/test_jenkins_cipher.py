import base64
import unittest

from jenkins_cipher import JenkinsCipher


class JenkinsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        master_key = (
            b"12780d3c3d93e23360dbe0e8750a9a1ba1c521baec776e956dc"
            b"214f32ade1f27a4956490a9152014d2944ab8b82261f17858926"
            b"5dd54ecd659eca965dbbf537c2aa08e10418de19bb96f4c44ed9"
            b"c42f702f7ca2fce790730dfad7f99cf0debc194508f3cde4baf6"
            b"01cc64f7efd0377259bcafa1ee9901efc900eb6a216740757"
        )
        hudson_secret_key = (
            b"\x65\x02\xbf\x0d\xa4\x37\x22\x6b\xb0\x40\xab\x19\x9c\xf1\xb2\x1b"
            b"\x6c\x3f\xa1\x5b\xab\x2f\x0b\x0f\xcc\x56\x36\xb6\xa0\x8d\x35\x98"
            b"\xc5\x14\x8a\xd9\x99\x53\xb6\x98\x59\x2f\x90\x81\x1c\x53\xc9\xe1"
            b"\x61\xc7\x61\x18\x1a\x06\x69\x49\x91\xf7\x59\x7d\xcd\xce\x07\x2e"
            b"\xd3\x9f\xee\xc3\x13\x18\x72\x7e\x47\x8f\xfe\x77\x9a\x95\x75\xf3"
            b"\x9b\x38\xc6\xde\xcd\x27\xf4\x95\x00\xd8\xac\x69\x3e\xfd\x04\xb1"
            b"\x1a\x41\x93\xe5\x27\xdd\xb7\x02\x28\xf0\x0c\x03\xa5\xa8\x69\x2d"
            b"\xeb\x57\x86\x77\x69\x37\xda\x5e\xf4\xdb\xdb\x1a\x28\x3b\x43\xef"
            b"\x56\x3d\x51\xf7\xa3\x1d\xd9\x04\xef\x77\x72\x1a\x8a\xd9\x31\x2f"
            b"\x11\xa8\x49\x83\xee\xbc\x8a\x40\x9d\xa4\xdf\x90\xd0\xa9\x36\x89"
            b"\x7b\x02\x4a\xeb\x83\x3c\xc9\xb9\x5f\xe1\x53\x26\xe9\x62\xe6\xe4"
            b"\x47\xa5\xdd\x3a\xc4\xda\x3b\xf5\x40\xd7\x13\xff\x2f\x50\x3e\x0b"
            b"\x3b\x16\xaa\x32\x1d\xdb\xd9\xec\x7e\x23\x22\x15\x23\x71\x87\xc6"
            b"\x61\x8a\xe6\xf6\xcf\xd3\x9c\xcb\x62\x9c\xa7\xb6\xf6\x98\xbf\x33"
            b"\x1b\x92\xa5\xf7\x04\xf4\x98\x3e\xfb\x42\x1a\x17\xd9\xb0\xcc\xe5"
            b"\xec\x7c\x8d\xd6\x7b\x17\xd3\xa5\x15\xa0\xb3\x69\x16\xdc\xbe\x3d"
            b"\x73\x77\x55\xe1\x45\x7d\x8b\x54\x3d\xe5\xfd\x0d\xe9\xb0\x8b\x71"
        )
        cls.dummy_password_encrypted = base64.decodebytes(
            b"S3utyMSH+P2IcVQNFtXTDKS3SJa9ZTsGOqquMmggSdA="
        )
        cls.dummy_password_plain = 'jenkins'
        cls.jenkins_cipher = JenkinsCipher(
            master_key=master_key,  hudson_secret_key=hudson_secret_key
        )

    def test_decrypt_old(self):
        self.assertEqual(
            self.jenkins_cipher.decrypt(self.dummy_password_encrypted),
            self.dummy_password_plain
        )

    def test_encrypt_old(self):
        encrypted_password = self.jenkins_cipher.encrypt(
            self.dummy_password_plain
        )
        self.assertEqual(self.dummy_password_encrypted, encrypted_password)
        self.assertEqual(
            self.jenkins_cipher.decrypt(encrypted_password),
            self.dummy_password_plain
        )

    def test_decrypt(self):
        encrypted = b"{AQAAABAAAAAg2nYSYPQRMrY5PZxLLuble6jVKmd7vn" \
                    b"VN9P2eCpUf6yi9HomkwaSQu8MKG5gBrgb0}"
        self.assertEqual(
            self.jenkins_cipher.decrypt(encrypted), "test encrypted text"
        )
