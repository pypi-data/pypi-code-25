from .decorators import (
    validate_conversion_arguments,
)
from .encoding import (
    big_endian_to_int,
    int_to_big_endian,
)
from .types import (
    is_boolean,
    is_integer,
    is_string,
)
from .hexadecimal import (
    add_0x_prefix,
    decode_hex,
    encode_hex,
    is_hex,
    remove_0x_prefix,
)


@validate_conversion_arguments
def to_hex(primitive=None, hexstr=None, text=None):
    """
    Auto converts any supported value into it's hex representation.

    Trims leading zeros, as defined in:
    https://github.com/ethereum/wiki/wiki/JSON-RPC#hex-value-encoding
    """
    if hexstr is not None:
        return add_0x_prefix(hexstr.lower())

    if text is not None:
        return encode_hex(text.encode('utf-8'))

    if is_boolean(primitive):
        return "0x1" if primitive else "0x0"

    if isinstance(primitive, (bytes, bytearray)):
        return encode_hex(primitive)
    elif is_string(primitive):
        raise TypeError(
            "Unsupported type: The primitive argument must be one of: bytes,"
            "bytearray, int or bool and not str"
        )

    if is_integer(primitive):
        return hex(primitive)

    raise TypeError(
        "Unsupported type: '{0}'.  Must be one of: bool, str, bytes, bytearray"
        "or int.".format(repr(type(primitive)))
    )


@validate_conversion_arguments
def to_int(primitive=None, hexstr=None, text=None):
    """
    Converts value to it's integer representation.

    Values are converted this way:

     * primitive:
       * bytes, bytearrays: big-endian integer
       * bool: True => 1, False => 0
     * hexstr: interpret hex as integer
     * text: interpret as string of digits, like '12' => 12
    """
    if hexstr is not None:
        return int(hexstr, 16)
    elif text is not None:
        return int(text)
    elif isinstance(primitive, (bytes, bytearray)):
        return big_endian_to_int(primitive)
    elif isinstance(primitive, str):
        raise TypeError("Pass in strings with keyword hexstr or text")
    else:
        return int(primitive)


@validate_conversion_arguments
def to_bytes(primitive=None, hexstr=None, text=None):
    if is_boolean(primitive):
        return b'\x01' if primitive else b'\x00'
    elif isinstance(primitive, bytearray):
        return bytes(primitive)
    elif isinstance(primitive, bytes):
        return primitive
    elif is_integer(primitive):
        return to_bytes(hexstr=to_hex(primitive))
    elif hexstr is not None:
        if len(hexstr) % 2:
            hexstr = '0x0' + remove_0x_prefix(hexstr)
        return decode_hex(hexstr)
    elif text is not None:
        return text.encode('utf-8')
    raise TypeError(
        "expected a bool, int, byte or bytearray in first arg, or keyword of hexstr or text"
    )


@validate_conversion_arguments
def to_text(primitive=None, hexstr=None, text=None):
    if hexstr is not None:
        return to_bytes(hexstr=hexstr).decode('utf-8')
    elif text is not None:
        return text
    elif isinstance(primitive, str):
        return to_text(hexstr=primitive)
    elif isinstance(primitive, (bytes, bytearray)):
        return primitive.decode('utf-8')
    elif is_integer(primitive):
        byte_encoding = int_to_big_endian(primitive)
        return to_text(byte_encoding)
    raise TypeError("Expected an int, bytes, bytearray or hexstr.")


def text_if_str(to_type, text_or_primitive):
    '''
    Convert to a type, assuming that strings can be only unicode text (not a hexstr)

    @param to_type is a function that takes the arguments (primitive, hexstr=hexstr, text=text),
        eg~ to_bytes, to_text, to_hex, to_int, etc
    @param hexstr_or_primitive in bytes, str, or int.
    '''
    if isinstance(text_or_primitive, str):
        (primitive, text) = (None, text_or_primitive)
    else:
        (primitive, text) = (text_or_primitive, None)
    return to_type(primitive, text=text)


def hexstr_if_str(to_type, hexstr_or_primitive):
    '''
    Convert to a type, assuming that strings can be only hexstr (not unicode text)

    @param to_type is a function that takes the arguments (primitive, hexstr=hexstr, text=text),
        eg~ to_bytes, to_text, to_hex, to_int, etc
    @param text_or_primitive in bytes, str, or int.
    '''
    if isinstance(hexstr_or_primitive, str):
        (primitive, hexstr) = (None, hexstr_or_primitive)
        if remove_0x_prefix(hexstr) and not is_hex(hexstr):
            raise ValueError(
                "when sending a str, it must be a hex string. Got: {0!r}".format(
                    hexstr_or_primitive,
                )
            )
    else:
        (primitive, hexstr) = (hexstr_or_primitive, None)
    return to_type(primitive, hexstr=hexstr)
