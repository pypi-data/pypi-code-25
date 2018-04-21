from Crypto.Cipher import AES

KEY = 'fdsl;mewrjope456fds4fbvfnjwaugfo'


def encrypt(message):
    message_length = len(message)
    if message_length % 16 != 0:
        message += '\0' * (16 - message_length % 16)
    aes = AES.new(KEY, AES.MODE_ECB)
    ciphertext = aes.encrypt(message)
    return ciphertext


def decrypt(message):
    aes = AES.new(KEY, AES.MODE_ECB)
    plaintext = aes.decrypt(message)
    return str(plaintext, encoding="utf-8").rstrip('\0')