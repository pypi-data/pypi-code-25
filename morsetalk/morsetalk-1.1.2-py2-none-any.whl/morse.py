# -*- coding: utf-8 -*-
from morsetalk.alphabet import CODE
from morsetalk.exceptions import MorseEncodeException, MorseDecodeException
import random


def new_char():
    morse = '.-'
    char = ''

    while char in CODE.values() or not char:
        char += morse[random.randint(0, len(morse) - 1)]

    return char


def encode_char(char):
    char = char.upper()

    if char not in CODE:
        raise MorseEncodeException(
            '<' + char + '> does not exist in the morse alphabet'
        )

    return CODE[char]


def decode_char(char):
    char = char.upper()

    if char not in CODE.values():
        raise MorseDecodeException(
            '<' + char + '> does not exist in the morse alphabet'
        )

    for k, v in CODE.items():
        if v == char:
            return k


def encode(string):
    encoded_string = ''

    for i, char in enumerate(string):
        encoded_string += encode_char(char)
        encoded_string += ' ' if i < len(string) - 1 else ''

    return encoded_string


def decode(string):
    decoded_string = ''

    for i, char in enumerate(string.split(' ')):
        decoded_string += decode_char(char)

    return decoded_string
