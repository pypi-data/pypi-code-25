import os
import sys
import base64
import argparse

import logging

from . cipher import JenkinsCipher


logging.basicConfig(level=logging.WARNING)


ACTION_ENCRYPT = 'encrypt'
ACTION_DECRYPT = 'decrypt'
ACTIONS = (
    ACTION_ENCRYPT, ACTION_DECRYPT
)
DEFAULT_ACTION = ACTION_ENCRYPT
EXIT_OK = 0


def get_absolute_path(relative_path, lower_case=True):
    """
    gets absolute path in respect of running operating system (useful to use
    it for volumes registration and so other basic operations)

    :param str relative_path: relative path to get absolute path for docker
        volume. Depending on OS it could be different.
    :param bool lower_case: cast lower case if True (default)
    :rtype: str
    :return: str
    """
    path = os.path.abspath(relative_path).replace('\\', '/')
    if lower_case:
        return path.lower()
    return path


def main(opts):
    master_key_location = get_absolute_path(opts.master_key)
    hudson_secret_key_location = get_absolute_path(opts.hudson_secret_key)
    master_key = open(master_key_location, 'rb').read()
    hudson_secret_key = open(hudson_secret_key_location, 'rb').read()
    cipher = JenkinsCipher(hudson_secret_key=hudson_secret_key,
                           master_key=master_key)
    for message in opts.messages:
        if opts.action == ACTION_ENCRYPT:
            encrypted = cipher.encrypt(message)
            print(base64.b64encode(encrypted).decode('utf-8'))
        elif opts.action == ACTION_DECRYPT:
            print(cipher.decrypt(base64.b64decode(message)))
        else:
            pass
    return EXIT_OK


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='jenkins_cipher',
        description='cipher operations (encrypt / decrypt)'
    )
    parser.add_argument(nargs='*', dest='messages', type=str,
                        help='passwords split by space to encrypt',
                        metavar='text')
    parser.add_argument(
        '--action', dest='action',
        choices=ACTIONS,
        default=DEFAULT_ACTION,
        help='action to perform, default is `%s`' % DEFAULT_ACTION,
        required=False
    )
    parser.add_argument('--master-key', dest='master_key',
                        required=True,
                        help='master key location')
    parser.add_argument('--hudson-secret-key', dest='hudson_secret_key',
                        help='hudson secret key')
    options = parser.parse_args()
    sys.exit(main(options))
