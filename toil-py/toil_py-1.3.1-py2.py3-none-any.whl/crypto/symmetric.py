# -*- coding: utf-8 -*-
""" Handle cryptology via symmetric algorithms. """
import codecs
import errno
import logging
import os

# from Crypto.Cipher import AES
# from Crypto.Random import get_random_bytes
from cryptography.fernet import Fernet

# constants
DEFAULT_BLOCK_SIZE = 32
DEFAULT_IV_SIZE = 16

logger = logging.getLogger(__name__)


class BaseSymmetricEncryptor(object):
    """
    Base class for symmetric encryption

    Properties:
      config: dict with configuration data
      encryption_key: base 64 encoded key
      encryption_iv: base 64 coded encoded initialization vector
    """

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    @property
    def encryption_key(self):
        return self._encryption_key

    @encryption_key.setter
    def encryption_key(self, value):
        if os.path.isfile(value):
            self.encryption_key = open(value, 'r').read()
        else:
            self._encryption_key = value

    @property
    def encryption_iv(self):
        return self._encryption_iv

    @encryption_iv.setter
    def encryption_iv(self, value):

        self._encryption_iv = value

    def __init__(self, config):
        """
        Initialize the encryptor
        Args:
          config (dict): Configuration for encryption
        """
        self._config = None
        self._encryption_key = None
        self._encryption_iv = None
        self.config = config
        logger.debug("config={config}".format(config=config))

    def generate_key(self, file_name=None, key_length=DEFAULT_BLOCK_SIZE):
        """
        Generate an encryption key.

        Args:
          file_name (str): optional file to write key to
          key_length (int): byte length of key

        Returns:
          A base 64 encoded key.
        """
        raise NotImplementedError

    def generate_iv(self, file_name=None, iv_length=DEFAULT_IV_SIZE):
        """
        Generate an encryption initialization vector.

        Args:
          file_name (str): optional file name
          iv_length (int): byte lengrh of iv

        Returns:
          A base 64 encoded initializstion vector.
        """
        raise NotImplementedError

    def encrypt(self, confidential_data, block_size=DEFAULT_BLOCK_SIZE):
        """
        Encrypt data with an symmetric algorithm.

        Args:
          confidential_data (str): data to be encrypted
          block_size (int): optional block size

        Returns:
          encrypted data
        """
        raise NotImplementedError

    def decrypt(self, encrypted_data, block_size=DEFAULT_BLOCK_SIZE):
        """
        Decrypt data witn a symmetric algorithm.

        Args:
          encrypted_data (str): data to decrypt
          block_size (int): optional block size

        Returns:
        """
        raise NotImplementedError


class SymmetricEncryptor(BaseSymmetricEncryptor):
    """
    Use AES symmetric encryption from the cryptography package

    See BaseSymmetricEncryptor for additional information.
    """

    def __init__(self, config):
        super(SymmetricEncryptor, self).__init__(config)

        if 'key' in config.keys():

            if os.path.isfile(config['key']):
                self.encryption_key = open(config['key'], 'r').read()
            else:
                self.encryption_key = config['key']


    def generate_key(self, file_name=None, key_length=DEFAULT_BLOCK_SIZE):

        key = Fernet.generate_key()

        if file_name is not None:
            if not os.path.exists(os.path.dirname(file_name)):
                try:
                    os.makedirs(os.path.dirname(file_name))

                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise

            logger.info('key file:{file_name}'.format(file_name=file_name))

            with codecs.open(file_name, 'a', 'utf-8') as f:
                f.write(key)
                f.write('\n')

        return key

    def encrypt(self, confidential_data, block_size=DEFAULT_BLOCK_SIZE, encryption_key=None, encryption_iv=None):

        if isinstance(confidential_data, unicode):
            confidential_data = str(confidential_data)

        if encryption_key is None:
            encryption_key = self.encryption_key
        else:
            encryption_key = encryption_key

        f = Fernet(encryption_key)
        encrypted_data = f.encrypt(confidential_data.encode("utf-8"))

        logger.debug('encrypted:{encrypted_data}'.format(encrypted_data=encrypted_data))

        return encrypted_data

    def decrypt(self, encrypted_data, block_size=DEFAULT_BLOCK_SIZE, encryption_key=None, encryption_iv=None):

        if isinstance(encrypted_data, unicode):
            encrypted_data = str(encrypted_data)

        logger.debug('decrypt:{encrypted_data}'.format(encrypted_data=encrypted_data))

        if encryption_key is None:
            encryption_key = self.encryption_key
        else:
            encryption_key = encryption_key

        f = Fernet(encryption_key)
        decrypted_data = f.decrypt(encrypted_data.encode("utf-8"))

        logger.debug('decrypt result:{decrypted_data}'.format(decrypted_data=decrypted_data))

        return decrypted_data

# class SymmetricEncryptor(BaseSymmetricEncryptor):
#   """
#   Implements AES CBC symmetric encryption
#
#   See BaseSymmetricEncryptor for additional information.
#   """
#
#   def __init__(self, config):
#     super(SymmetricEncryptor, self).__init__(config)
#
#     if 'key' in config.keys():
#       self.encryption_key = config['key']
#
#     if 'iv' in config.keys():
#       self.encryption_iv = config['iv']
#
#   def generate_key(self, file_name=None, key_length=DEFAULT_BLOCK_SIZE):
#    key = get_random_bytes(key_length)
#    b64_key = base64.urlsafe_b64encode(key)
#
#    if file_name is not None:
#      logger.info('key file:{file_name}'.format(file_name=file_name))
#      with codecs.open(file_name, 'a', 'utf-8') as f:
#        f.write(b64_key)
#        f.write('\n')
#
#    return b64_key
#
#   def generate_iv(self, file_name=None, iv_length=DEFAULT_IV_SIZE):
#     iv = get_random_bytes(iv_length)
#     b64_iv = base64.urlsafe_b64encode(iv)
#     if file_name is not None:
#       logger.info('key file:{file_name}'.format(file_name=file_name))
#       with codecs.open(file_name, 'a', 'utf-8') as f:
#         f.write(b64_iv)
#         f.write('\n')
#     return b64_iv
#
#   def encrypt(self, confidential_data, block_size=DEFAULT_BLOCK_SIZE, encryption_key=None, encryption_iv=None):
#
#     if isinstance(confidential_data, unicode):
#       confidential_data = str(confidential_data)
#
#     if encryption_key is None:
#       encryption_key = base64.urlsafe_b64decode(self.encryption_key.encode("utf-8"))
#     else:
#       encryption_key = base64.urlsafe_b64decode(encryption_key.encode("utf-8"))
#
#     if encryption_iv is None:
#       encryption_iv = base64.urlsafe_b64decode(self.encryption_iv.encode("utf-8"))
#     else:
#       encryption_iv = base64.urlsafe_b64decode(encryption_iv.encode("utf-8"))
#
#     def pad(s): return s + (block_size - len(s) % block_size) * chr(block_size - len(s) % block_size)
#     cipher = AES.new(encryption_key, AES.MODE_CBC, iv=encryption_iv)
#     encrypted_data = cipher.encrypt(pad(confidential_data))
#     b64_encrypted_data = base64.urlsafe_b64encode(encrypted_data)
#     logger.debug('encrypted:{encrypted_data}'.format(encrypted_data=b64_encrypted_data))
#     return b64_encrypted_data
#
#   def decrypt(self, encrypted_data, block_size=DEFAULT_BLOCK_SIZE, encryption_key=None, encryption_iv=None):
#
#     if isinstance(encrypted_data, unicode):
#      encrypted_data = str(encrypted_data)
#
#     logger.debug('decrypt:{encrypted_data}'.format(encrypted_data=encrypted_data))
#
#     if encryption_key is None:
#       encryption_key = base64.urlsafe_b64decode(self.encryption_key.encode("utf-8"))
#     else:
#       encryption_key = base64.urlsafe_b64decode(encryption_key.encode("utf-8"))
#
#     if encryption_iv is None:
#       encryption_iv = base64.urlsafe_b64decode(self.encryption_iv.encode("utf-8"))
#     else:
#       encryption_iv = base64.urlsafe_b64decode(encryption_iv.encode("utf-8"))
#
#     def unpad(s): return s[:-ord(s[len(s)-1:])]
#     cipher = AES.new(encryption_key, AES.MODE_CBC, iv=encryption_iv)
#
#     decoded_encrypted_data = base64.urlsafe_b64decode(encrypted_data.encode("utf-8"))
#     decrypted_data = unpad(cipher.decrypt(decoded_encrypted_data))
#
#     logger.debug('decrypt result:{decrypted_data}'.format(decrypted_data=decrypted_data))
#
#     return decrypted_data
