import os
import re
import glob
import json
import base64
import logging
import pyaes
from localstack.utils.common import safe_requests as requests
from localstack.utils.common import load_file, save_file, to_str
from localstack_ext import config
from localstack_ext.config import PROTECTED_FOLDERS, ROOT_FOLDER, VERSION

ENV_PREPARED = {}


def read_license_key():
    key = os.environ.get('LICENSE_KEY')
    if key:
        return key
    raise Exception('Unable to retrieve license key. Please configure $LICENSE_KEY in your environment')


def fetch_key():
    license_key = read_license_key()
    data = {
        'license_key': license_key,
        'version': VERSION
    }
    try:
        # temporarily disable urllib3 warnings (SSL validation)
        logging.getLogger('py.warnings').setLevel(logging.ERROR)
        result = requests.post('%s/activate' % config.API_URL, json.dumps(data))
    finally:
        logging.getLogger('py.warnings').setLevel(logging.WARNING)
    key_base64 = json.loads(result.content)['key']
    decoded_key = to_str(base64.b64decode(key_base64))
    return decoded_key


def generate_aes_cipher(key):
    return pyaes.AESModeOfOperationCBC(key, iv='\0' * 16)


def decrypt_file(source, target, key):
    cipher = generate_aes_cipher(key)
    raw = load_file(source, mode='rb')
    decrypter = pyaes.Decrypter(cipher)
    decrypted = decrypter.feed(raw)
    decrypted += decrypter.feed()
    decrypted = decrypted.partition(b'\0')[0]
    decrypted = to_str(decrypted)
    save_file(target, content=decrypted)


def decrypt_files(key):
    for folder in PROTECTED_FOLDERS:
        for subpath in ('*.py.enc', '**/*.py.enc'):
            for f in glob.glob('%s/localstack_ext/%s/%s' % (ROOT_FOLDER, folder, subpath)):
                target = f[:-4]
                decrypt_file(f, target, key)


def cleanup_environment():
    excepted_files = r'.*/services/((edge)|(dns_server)|(__init__))\.py'
    for folder in PROTECTED_FOLDERS:
        for subpath in ('*.py.enc', '**/*.py.enc'):
            for f in glob.glob('%s/localstack_ext/%s/%s' % (ROOT_FOLDER, folder, subpath)):
                target = f[:-4]
                if not re.match(excepted_files, target):
                    for delete_file in (target, '%sc' % target):
                        if os.path.exists(delete_file):
                            os.remove(delete_file)


def prepare_environment():

    class OnClose(object):

        def __exit__(self, *args, **kwargs):
            if not ENV_PREPARED.get('done'):
                cleanup_environment()
            ENV_PREPARED['done'] = True

        def __enter__(self, *args, **kwargs):
            pass

    if not ENV_PREPARED.get('done'):
        try:
            key = fetch_key()
            decrypt_files(key)
        except Exception as e:
            # for now we fail silently, but in the future we may want to print
            # a meaningful log message here (asking the user to set $LICENSE_KEY)
            pass

    return OnClose()
