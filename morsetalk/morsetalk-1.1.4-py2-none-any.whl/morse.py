# -*- coding: utf-8 -*-
from morsetalk.alphabet import CODE
from morsetalk.exceptions import MorseEncodeException, MorseDecodeException


def encode_char(char):
    if not char:
        return ''

    char = char.upper()

    if char not in CODE:
        raise MorseEncodeException(
            '<' + char + '> does not exist in the morse alphabet'
        )

    return CODE[char]


def decode_char(char):
    if not char:
        return ''

    char = char.upper()

    if char not in CODE.values():
        raise MorseDecodeException(
            '<' + char + '> does not exist in the morse alphabet'
        )

    return filter(lambda x: x[1] == char, CODE.items())[0][0]


def encode(string):
    return ''.join([encode_char(char) + (' ' if i < len(string) - 1 else '')
                    for i, char in enumerate(string)])


def decode(string):
    return ''.join([decode_char(char) for char in string.split(' ')])
