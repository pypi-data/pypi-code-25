from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
import base64
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_rsa_cipher(is_sandbox=False):
    if is_sandbox:
        path = os.path.join(BASE_DIR, 'dapp_sb.pem')
    else:
        path = os.path.join(BASE_DIR, 'dapp_prod.pem')

    with open(path, 'r') as myfile:
        data = myfile.read()

    private_key = RSA.importKey(data)
    cipher_rsa = PKCS1_OAEP.new(private_key)
    return cipher_rsa


def encrypt_rsa(value, _is_sandbox=None):
    if _is_sandbox is None:
        from dappmx import is_sandbox
        _is_sandbox = is_sandbox

    cipher_rsa = get_rsa_cipher(_is_sandbox)

    encrypted_bytes = cipher_rsa.encrypt(value.encode('utf-8'))
    encrypted_b64string = base64.b64encode(encrypted_bytes).decode('utf-8')
    return encrypted_b64string
