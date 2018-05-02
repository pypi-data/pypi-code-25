"""
Generates cryptographic keys.



Key types
---------

* Secret keys (either randomly generated or deterministic, based on a password).
* Public-Private key pairs.


How to use keys
---------------

* Secret keys are used for encryption (see Crypto).
* Secret keys are also used to secure other secret keys and private keys (see KeyWrapper)
* Public-Private keys are used for digital signatures (see DigitalSignature).
* Public-Private keys are also used for key exchange (see KeyExchange).


Managing encryption keys
------------------------

A good applied cryptography design is all about how you manage secrets: keys and passwords.

Assuming you're using primitives correctly (that's what Cryptolite does for you)
then it'll be all about your key management design.

Here are some examples, based on using secret keys to encrypt user data,
to give you a primer on the things you'll want to consider when designing with encryption.
In these examples, we're choosing between random and deterministic (password-based) keys.


Deterministic key design
------------------------

Deterministic keys are the easiest to manage as you don't need to store the key itself.
Providing the password used to generate the key is properly managed and is available
when you need access to the key, the key can be reliably regenerated each time.

The drawback is that if you want to generate more than one key you'll need more than one password.
However, if you do only need one key, this approach can be ideal as you could use, say, the user's
plaintext password to generate the key. You never store a user's plaintext password (see
``password.hash``) so the right key can only be generated when the user logs in.

Bear in mind however that if the user changes (or resets) their password this will generate a
different key, so you'll need a plan for recovering data encrypted with the old key and
re-encrypting it with the new one.


Random key design
-----------------

Random keys are simple to generate, but need to be stored because there's no way
to regenerate the same key.

To store a key you can use ``key_wrapper.wrapSecretKey()``.
This encrypts the key which means it can be safely stored in, for example,
a database or configuration value.

The benefit of the ``key_wrapper`` approach is that
when a user changes their password you'll only need to re-encrypt the stored keys using a new
``key_wrapper`` initialised with the new password, rather than have to re-encrypt all
data that was encrypted with a key generated based on the user's password
(as in a deterministic design).


Password recovery and reset
---------------------------

In both designs, when a user changes their password you will have the old and the new plaintext
passwords, meaning you can decrypt with the old an re-encrypt with the new.

The difficulty comes when you need to reset a password, because it's not possible to recover
the old password, so you can't recover the encryption key either. In this case you'll either
need a backup way to recover the encryption key, or you'll need to be clear that data cannot
be recovered at all.

Whatever your solution, remember that storing someone's password in any recoverable form is not OK,
so you'll need to put some thought into the recovery process.

"""

import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptolite import byte_array

__author__ = "David Carboni"

backend = default_backend()

# Please treat the following values as constants.
# They are implemented as variables just in case you do need to alter them.
# These are the settings that provide "right" cryptography so you'll need to
# know what you're doing if you want to alter them.

"""The secret key algorithm."""
SYMMETRIC_ALGORITHM = "AES"

"""The key size for secret keys."""
SYMMETRIC_KEY_SIZE = 256

"""The algorithm to use to generate password-based secret keys."""
SYMMETRIC_PASSWORD_ALGORITHM = "PBKDF2WithHmacSHA1"

"""The number of iteration rounds to use for password-based secret keys."""
SYMMETRIC_PASSWORD_ITERATIONS = 1024

"""The public-private key pair algorithm."""
ASYMMETRIC_ALGORITHM = "RSA"

"""The key size for public-private key pairs."""
ASYMMETRIC_KEY_SIZE = 4096


def new_secret_key():
    """
    Generates a new secret (also known as symmetric) key for use with AES.

    The key size is determined by SYMMETRIC_KEY_SIZE.

    :return: A new, randomly generated secret key.
    """
    # FYI: AES keys are just random bytes from a strong source of randomness.
    return os.urandom(SYMMETRIC_KEY_SIZE // 8)


def generate_secret_key(password, salt):
    """
    Generates a new secret (or symmetric) key for use with AES using the given password and salt values.

    Given the same password and salt, this method will always (re)generate the same key.

    :param password: The starting point to use in generating the key. This can be a password, or any
                    suitably secret string. It's worth noting that, if a user's plaintext password is
                    used, this makes key derivation secure, but means the key can never be recovered
                    if a user forgets their password. If a different value, such as a password hash is
                    used, this is not really secure, but does mean the key can be recovered if a user
                    forgets their password. It's all about risk, right?
    :param salt:     A value for this parameter can be generated by calling
                    ``generate.salt()``. You'll need to store the salt value (this is ok to do
                    because salt isn't particularly sensitive) and use the same salt each time in
                    order to always generate the same key. Using salt is good practice as it ensures
                    that keys generated from the same password will be different - i.e. if two users
                    use the password, having a salt value avoids the generated keys being
                    identical which might give away someone's password.
    :return: A deterministic secret key, defined by the given password and salt
    """
    if password is None:
        return None
    salt_bytes = bytes(byte_array.from_base64(salt))
    key_generator = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=SYMMETRIC_KEY_SIZE // 8,
        salt=salt_bytes,
        iterations=SYMMETRIC_PASSWORD_ITERATIONS,
        backend=backend
    )
    password_bytes = password.encode("utf-8")
    return key_generator.derive(password_bytes)


def new_key_pair():
    """
    Generates a new public-private (or asymmetric) key pair for use with ASYMMETRIC_ALGORITHM.

    The key size will be ASYMMETRIC_KEY_SIZE bits.

    :return: A new, randomly generated asymmetric key pair.
    """
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=ASYMMETRIC_KEY_SIZE,
        backend=default_backend()
    )
