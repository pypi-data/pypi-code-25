#!/usr/bin/env python
# coding=utf-8
'''
A literal implementation of the whatwg url parsing state machine.
https://url.spec.whatwg.org/#concept-basic-url-parser
'''

import re
import idna
import sys

try:
    unicode
except NameError:
    unicode = str

SPECIAL_SCHEMES = {
    u'ftp': 21,
    u'file': None,
    u'gopher': 70,
    u'http': 80,
    u'https': 443,
    u'ws': 80,
    u'wss': 443,
}
ASCII_ALPHA_UPPER_RE = re.compile(u'\\A[A-Z]\\Z')
ASCII_ALPHA_LOWER_RE = re.compile(u'\\A[a-z]\\Z')
ASCII_ALPHA_RE = re.compile(u'\\A[A-Za-z]\\Z')
ASCII_DIGIT_RE = re.compile(u'\\A[0-9]\\Z')
ASCII_HEX_DIGIT_RE = re.compile(u'\\A[0-9A-Fa-f]\\Z')
ASCII_ALPHANUMERIC_RE = re.compile(u'\\A[0-9A-Za-z]\\Z')

# A C0 control is a code point in the range U+0000 to U+001F, inclusive.
# The simple encode set are C0 controls and all code points greater than
# U+007E.
C0_CONTROL_ENCODE_SET = re.compile(
        u'\\A[\u0000-\u001f\u007f-\U0010ffff]\\Z')
# The default encode set is the simple encode set and code points U+0020,
# '"', "#", "<", ">", "?", "`", "{", and "}".
DEFAULT_ENCODE_SET_RE = re.compile(
         u'\\A[\u0000-\u0020\u007f-\U0010ffff"#<>?`{}]\\Z')
# The userinfo encode set is the default encode set and code points "/",
# ":", ";", "=", "@", "[", "\", "]", "^", and "|".
USERINFO_ENCODE_SET_RE = re.compile(
        u'\\A[]\u0000-\u0020\u007f-\U0010ffff"#<>?`{}/:;=@[\^|]\\Z')

# The URL code points are ASCII alphanumeric, "!", "$", "&", "'", "(", ")",
# "*", "+", ",", "-", ".", "/", ":", ";", "=", "?", "@", "_", "~", and code
# points in the ranges U+00A0 to U+D7FF, U+E000 to U+FDCF, U+FDF0 to
# U+FFFD, U+10000 to U+1FFFD, U+20000 to U+2FFFD, U+30000 to U+3FFFD,
# U+40000 to U+4FFFD, U+50000 to U+5FFFD, U+60000 to U+6FFFD, U+70000 to
# U+7FFFD, U+80000 to U+8FFFD, U+90000 to U+9FFFD, U+A0000 to U+AFFFD,
# U+B0000 to U+BFFFD, U+C0000 to U+CFFFD, U+D0000 to U+DFFFD, U+E0000 to
# U+EFFFD, U+F0000 to U+FFFFD, U+100000 to U+10FFFD.
# XXX py2 doesn't like this regex
# URL_CODEPOINT_RE = re.compile(
#         u"\\A[-a-zA-Z0-9!$&'()*+,./:;=?@_~\u00a0-\ud7ff\ue000-\ufdcf"
#         u"\ufdf0-\ufffd\U00010000-\U0001fffd\U00020000-\U0002fffd"
#         u"\U00030000-\U0003fffd\U00040000-\U0004fffd\U00050000-\U0005fffd"
#         u"\U00060000-\U0006fffd\U00070000-\U0007fffd\U00080000-\U0008fffd"
#         u"\U00090000-\U0009fffd\U000a0000-\U000afffd\U000b0000-\U000bfffd"
#         u"\U000c0000-\U000cfffd\U000d0000-\U000dfffd\U000e0000-\U000efffd"
#         u"\U000f0000-\U000ffffd\U00100000-\U0010fffd]\\Z")
BMP_URL_CODEPOINT_RE = re.compile(
        u"\\A[-a-zA-Z0-9!$&'()*+,./:;=?@_~\u00a0-\ud7ff\ue000-\ufdcf"
        u"\ufdf0-\ufffd]\\Z")
def is_url_codepoint(c):
    return bool(BMP_URL_CODEPOINT_RE.match(c)) or (
            ord(c) >= 0x10000 and ord(c) <= 0x10ffff
            and not (ord(c) & 0xffff) in (0xfffe, 0xffff))

class URL:
    '''
    A URL is a universal identifier. To disambiguate from a URL string it can
    also be referred to as a URL record.

    A URL’s scheme is an ASCII string that identifies the type of URL and can
    be used to dispatch a URL for further processing after parsing. It is
    initially the empty string.

    A URL’s username is an ASCII string identifying a user. It is initially the
    empty string.

    A URL’s password is either null or an ASCII string identifying a user’s
    credentials. It is initially null.

    A URL’s host is either null or a host. It is initially null.

    A URL’s port is either null or a 16-bit unsigned integer that identifies a
    networking port. It is initially null.

    A URL’s path is a list of zero or more ASCII string holding data, usually
    identifying a location in hierarchical form. It is initially the empty
    list.

    A URL’s query is either null or an ASCII string holding data. It is
    initially null.

    A URL’s fragment is either null or a string holding data that can be used
    for further processing on the resource the URL’s other components identify.
    It is initially null.
    Note: This is not an ASCII string on purpose.

    A URL also has an associated cannot-be-a-base-URL flag. It is initially
    unset.

    A URL also has an associated object that is null, a Blob object, a
    MediaSource object, or a MediaStream object. It is initially null.
    [FILEAPI] [MEDIA-SOURCE] [MEDIACAPTURE-STREAMS]
    Note: At this point this is used primarily to support "blob" URLs, but
    others can be added going forward, hence "object".
    '''

    def __init__(self):
        self.scheme = u''
        self.username = u''
        self.password = None
        self.host = None
        self.port = None
        self.path = []
        self.query = None
        self.fragment = None
        self.cannot_be_a_base_url = False
        self.object = None

    def __repr__(self):
        return str(vars(self))

    def is_special(self):
        return self.scheme in SPECIAL_SCHEMES

    def shorten_path(self):
        '''
        To shorten a url’s path, if url’s scheme is not "file" or url’s path
        does not contain a single string that is a normalized Windows drive
        letter, remove url’s path’s last string, if any.
        '''
        if len(self.path) > 0 and (
                self.scheme != u'file' or len(self.path) > 1
                or not is_normalized_windows_drive_letter(self.path[0])):
            self.path.pop()

    def serialize_host(self):
        # The host serializer takes a host host and then runs these steps:
        # 1. If host is an IPv4 address, return the result of running the IPv4
        # serializer on host.
        if isinstance(self.host, int):
            return self.serialize_ipv4()
        # 2. Otherwise, if host is an IPv6 address, return "[", followed by the
        # result of running the IPv6 serializer on host, followed by "]".
        elif isinstance(self.host, IPv6Address):
            return '[' + self.host.serialize() + ']'
        # 3. Otherwise, host is a domain, return host.
        else:
            return self.host

    def serialize_ipv4(self):
        # 1. Let output be the empty string.
        output = u''
        # 2. Let n be the value of address.
        n = self.host
        # 3. Repeat four times:
        for i in range(4):
            # 1. Prepend n % 256, serialized, to output.
            output = unicode(n % 256) + output
            # 2. Unless this is the fourth time, prepend "." to output.
            if i < 3:
                output = u'.' + output
            # 3. Set n to floor(n / 256).
            n = n // 256
        # 4. Return output.
        return output

    def serialize(self, exclude_fragment=False):
        # The URL serializer takes a URL url, an optional exclude fragment
        # flag, and then runs these steps:
        # 1. Let output be url’s scheme and ":" concatenated.
        output = self.scheme + u':'
        # 2. If url’s host is non-null:
        if self.host is not None:
            # 1. Append "//" to output.
            output += u'//'
            # 2. If url’s username is not the empty string or url’s password is
            # non-null, run these substeps:
            if self.username != u'' or self.password is not None:
                # 1. Append url’s username to output.
                output += self.username
                # 2. If url’s password is non-null, append ":", followed by
                # url’s password, to output.
                if self.password is not None:
                    output += u':' + self.password
                # 3. Append "@" to output.
                output += u'@'
            # 3. Append url’s host, serialized, to output.
            output += self.serialize_host()
            # 4. If url’s port is non-null, append ":" followed by url’s port,
            # serialized, to output.
            if self.port is not None:
                output += u':' + unicode(self.port)
        # 3. Otherwise, if url’s host is null and url’s scheme is "file",
        # append "//" to output.
        if self.host is None and self.scheme == u'file':
            output += u'//'
        # 4. If url’s cannot-be-a-base-URL flag is set, append the first string
        # in url’s path to output.
        if self.cannot_be_a_base_url:
            output += self.path[0]
        # 5. Otherwise, append "/", followed by the strings in url’s path
        # (including empty strings), separated from each other by "/", to
        # output.
        else:
            output += u'/'
            output += u'/'.join(self.path)
        # 6. If url’s query is non-null, append "?", followed by url’s query,
        # to output.
        if self.query is not None:
            output += u'?' + self.query
        # 7. If the exclude fragment flag is unset and url’s fragment is
        # non-null, append "#", followed by url’s fragment, to output.
        if not exclude_fragment and self.fragment is not None:
            output += u'#' + self.fragment
        # 8. Return output.
        return output

def is_windows_drive_letter(seg):
    '''
    A Windows drive letter is two code points, of which the first is an ASCII
    alpha and the second is either ":" or "|".
    '''
    return len(seg) == 2 and ASCII_ALPHA_RE.match(seg[:1]) and (
            seg[1:] == u':' or seg[1:] == u'|')

def is_normalized_windows_drive_letter(seg):
    '''
    A normalized Windows drive letter is a Windows drive letter of which the
    second code point is ":".
    '''
    return is_windows_drive_letter(seg) and seg[1:2] == u':'

def is_single_dot_path_segment(seg):
    '''
    A single-dot path segment must be "." or an ASCII case-insensitive match
    for "%2e".
    '''
    return seg in (u'.', u'%2e', u'%2E')

def is_double_dot_path_segment(seg):
    '''
    A double-dot path segment must be ".." or an ASCII case-insensitive match
    for ".%2e", "%2e.", or "%2e%2e".
    '''
    return re.match(u'\\A([.]|%2e){2}\\Z', seg, re.IGNORECASE)

# don't need this because we only lowercase stuff we already know is ascii
# ASCII_LOWER_TRANS = {ord(c): c.lower() for c in u'ABCDEFGHIJKLMNOPQRSTUVWXYZ'}
# def ascii_lowercase(s):
#     return s.translate(ASCII_LOWER_TRANS)

def utf8_pct_encode(codepoint, encode_set_re=DEFAULT_ENCODE_SET_RE):
    '''
    To UTF-8 percent encode a codePoint, using an encode set, run these steps:
        1. If codePoint is not in encode set, return codePoint.
        2. Let bytes be the result of running UTF-8 encode on codePoint.
        3. Percent encode each byte in bytes, and then return the results
           concatenated, in the same order.
    '''
    assert len(codepoint) == 1
    if not encode_set_re.match(codepoint):
        return codepoint
    _bytes = codepoint.encode('utf-8')
    encoded_bytes = []
    for i in range(len(_bytes)):
        b = _bytes[i:i+1]
        encoded_bytes.append(u'%%%02X' % ord(b))
    return u''.join(encoded_bytes)

class TerminateAlgorithm(Exception):
    pass
class Failure(Exception):
    pass

class ValidationErrorFlag:
    def __init__(self):
        self.validation_error = False
    def set(self):
        self.validation_error = True
    def is_set(self):
        return self.validation_error

HEX_DIGIT_BYTE_RE = re.compile(b'\\A[0-9A-Fa-f]\\Z')
def pct_decode(input):
    '''
    To percent decode a byte sequence input, run these steps:
    Warning: Using anything but UTF-8 decode without BOM when the input
    contains bytes that are not ASCII bytes might be insecure and is not
    recommended.
    1. Let output be an empty byte sequence.
    2. For each byte byte in input, run these steps:
       1. If byte is not `%`, append byte to output.
       2. Otherwise, if byte is `%` and the next two bytes after byte in input
          are not in the ranges 0x30 to 0x39, 0x41 to 0x46, and 0x61 to 0x66,
          append byte to output.
       3. Otherwise, run these substeps:
          1. Let bytePoint be the two bytes after byte in input, decoded, and
             then interpreted as hexadecimal number.
          2. Append a byte whose value is bytePoint to output.
          3. Skip the next two bytes in input.
    3. Return output.
    '''
    output = b''
    i = 0
    # for i in range(len(input)):
    while i < len(input):
        byte = input[i:i+1]
        if byte != b'%':
            output += byte
        elif byte == b'%' and not (
                HEX_DIGIT_BYTE_RE.match(input[i+1:i+2])
                and HEX_DIGIT_BYTE_RE.match(input[i+2:i+3])):
            output += byte
        else:
            bytepoint = int(input[i+1:i+3], 16)
            output += bytes([bytepoint])
            i += 2
        i += 1
    return output

# An IPv6 address is a 128-bit identifier and for the purposes of this specification represented as an ordered list of eight 16-bit pieces. [RFC4291]
# Note: Support for <zone_id> is intentionally omitted.
class IPv6Address(object):
    def __init__(self):
        self.pieces = [0, 0, 0, 0, 0, 0, 0, 0]
    # def first_longest_zero_sequence_piece_pointer(self):
    #     import pdb; pdb.set_trace()
    #     longest_start = None
    #     longest_len = 0
    #     seq_start = None
    #     seq_end = None
    #     for i in range(len(self.pieces)):
    #         if self.pieces[i] == 0:
    #             seq_end = i
    #             if seq_start is None:
    #                 seq_start = i
    #             if longest_start is None or seq_end - seq_start + 1 > longest_len:
    #                 longest_start = seq_start
    #                 longest_len = seq_end - seq_start + 1
    #         else:
    #             seq_start = None
    #             seq_end = None
    #     if longest_len < 2:
    #         return None
    #     else:
    #         return longest_start

    # function findLongestZeroSequence(arr) {
    #   let maxIdx = null;
    #   let maxLen = 1; // only find elements > 1
    #   let currStart = null;
    #   let currLen = 0;
    #
    #   for (let i = 0; i < arr.length; ++i) {
    #     if (arr[i] !== 0) {
    #       if (currLen > maxLen) {
    #         maxIdx = currStart;
    #         maxLen = currLen;
    #       }
    #
    #       currStart = null;
    #       currLen = 0;
    #     } else {
    #       if (currStart === null) {
    #         currStart = i;
    #       }
    #       ++currLen;
    #     }
    #   }
    #
    #   // if trailing zeros
    #   if (currLen > maxLen) {
    #     maxIdx = currStart;
    #     maxLen = currLen;
    #   }
    #
    #   return {
    #     idx: maxIdx,
    #     len: maxLen
    #   };
    # }
    def find_longest_zero_sequence(self):
        max_idx = None
        max_len = 1
        curr_start = None
        curr_len = 0
        for i in range(len(self.pieces)):
            if self.pieces[i] != 0:
                if curr_len > max_len:
                    max_idx = curr_start
                    max_len = curr_len
                curr_start = None
                curr_len = 0
            else:
                if curr_start is None:
                    curr_start = i
                curr_len += 1
        # if trailing zeroes
        if curr_len > max_len:
            max_idx = curr_start
            max_len = curr_len
        return {'idx': max_idx, 'len': max_len}

    def serialize(self):
        # ported from javascript at https://github.com/jsdom/whatwg-url/blob/master/src/url-state-machine.js
        output = ''
        seq_result = self.find_longest_zero_sequence()
        compress_pointer = seq_result['idx']
        for i in range(len(self.pieces)):
            if compress_pointer == i:
                if i == 0:
                    output += '::'
                else:
                    output += ':'
                i += seq_result['len'] - 1
                continue
            output += '%x' % self.pieces[i]
            if i != len(self.pieces) - 1:
                output += ':'
        return output

    # function serializeIPv6(address) {
    #   let output = "";
    #   const seqResult = findLongestZeroSequence(address);
    #   const compressPtr = seqResult.idx;
    #
    #   for (let i = 0; i < address.length; ++i) {
    #     if (compressPtr === i) {
    #       if (i === 0) {
    #         output += "::";
    #       } else {
    #         output += ":";
    #       }
    #
    #       i += seqResult.len - 1;
    #       continue;
    #     }
    #
    #     output += address[i].toString(16);
    #     if (i !== address.length - 1) {
    #       output += ":";
    #     }
    #   }
    #
    #   return output;
    # }
    # def serialize(self):
    #     # The IPv6 serializer takes an IPv6 address address and then runs these
    #     # steps:
    #     # 1. Let output be the empty string.
    #     output = u''
    #     # 2. Let compress pointer be a pointer to the first 16-bit piece in the
    #     # first longest sequences of address’s 16-bit pieces that are 0.
    #     # Example: In 0:f:0:0:f:f:0:0 it would point to the second 0.
    #     # 3. If there is no sequence of address’s 16-bit pieces that are 0
    #     # longer than one, set compress pointer to null.
    #     compress_pointer = self.first_longest_zero_sequence_piece_pointer()
    #     # 4. For each piece in address’s pieces, run these substeps:
    #     for piece_pointer in range(len(self.pieces)):
    #         # 1. If compress pointer points to piece, append "::" to output if
    #         # piece is address’s first piece and append ":" otherwise, and then
    #         # run these substeps again with all subsequent pieces in address’s
    #         # pieces that are 0 skipped or go the next step in the overall set
    #         # of steps if that leaves no pieces.
    #         if compress_pointer == piece_pointer:
    #             if piece_pointer == 0:
    #                 output += u'::'
    #             else:
    #                 output += u':'

def parse_ipv6(input, validation_error_flag):
    # 1. Let address be a new IPv6 address with its 16-bit pieces initialized
    # to 0.
    address = IPv6Address()

    # 2. Let piece pointer be a pointer into address’s 16-bit pieces, initially
    # zero (pointing to the first 16-bit piece), and let piece be the 16-bit
    # piece it points to.
    piece_pointer = 0

    # 3. Let compress pointer be another pointer into address’s 16-bit pieces,
    # initially null and pointing to nothing.
    compress_pointer = None

    # 4. Let pointer be a pointer into input, initially zero (pointing to the
    # first code point).
    pointer = 0

    # 5. If c is ":", run these substeps:
    if input[pointer:pointer+1] == u':':
        # 1. If remaining does not start with ":", validation error, return
        # failure.
        if input[pointer+1:pointer+2] != u':':
            validation_error_flag.set()
            return Failure
        # 2. Increase pointer by two.
        pointer += 2
        # 3. Increase piece pointer by one and then set compress pointer to
        # piece pointer.
        piece_pointer += 1
        compress_pointer = piece_pointer

    # 6. Main: While c is not the EOF code point, run these substeps:
    while input[pointer:pointer+1] != u'':
        # 1. If piece pointer is eight, validation error, return failure.
        if piece_pointer == 8:
            validation_error_flag.set()
            return Failure
        # 2. If c is ":", run these inner substeps:
            # 1. If compress pointer is non-null, validation error, return
            # failure.
            if compress_pointer is not None:
                validation_error_flag.set()
                return Failure
            # 2. Increase pointer and piece pointer by one, set compress
            # pointer to piece pointer, and then jump to Main.
            pointer += 1
            piece_pointer += 1
            compress_pointer = piece_pointer
            continue
        # 3. Let value and length be 0.
        value = 0
        length = 0
        # 4. While length is less than 4 and c is an ASCII hex digit, set value
        # to value × 0x10 + c interpreted as hexadecimal number, and increase
        # pointer and length by one.
        while length < 4 and ASCII_HEX_DIGIT_RE.match(input[pointer:pointer+1]):
            value = value * 0x10 + int(input[pointer:pointer+1], 16)
            pointer += 1
            length += 1
        jump_to_ipv4 = False
        # 5. Switching on c:
        # ↪ "."
        if input[pointer:pointer+1] == u'.':
            # 1. If length is 0, validation error, return failure.
            if length == 0:
                validation_error_flag.set()
                return Failure
            # 2. Decrease pointer by length.
            pointer -= length
            # 3. Jump to IPv4.
            jump_to_ipv4 = True
        # ↪ ":"
        elif input[pointer:pointer+1] == u':':
            # 1. Increase pointer by one.
            pointer += 1
            # 2. If c is the EOF code point, validation error, return failure.
            if input[pointer:pointer+1] == u'':
                validation_error_flag.set()
                return Failure
        # ↪ Anything but the EOF code point
        elif input[pointer:pointer+1] != u'':
            # Validation error, return failure.
            validation_error_flag.set()
            return Failure
        # 6. Set piece to value.
        address.pieces[piece_pointer] = value
        # 7. Increase piece pointer by one.
        piece_pointer += 1
    # 7. If c is the EOF code point, jump to Finale.
    if not jump_to_ipv4 and input[pointer:pointer+1] == u'':
    # 8. IPv4: If piece pointer is greater than six, validation error, return
    # failure.
        if piece_pointer > 6:
            validation_error_flag.set()
            return Failure
    # 9. Let numbersSeen be 0.
        numbers_seen = 0
    # 10. While c is not the EOF code point, run these substeps:
        while input[pointer:pointer+1] == u'':
            # 1. Let value be null.
            value = None
            # 2. If numbersSeen is greater than 0, then:
            if numbers_seen > 0:
                # 1. If c is a "." and numbersSeen is less than 4, then
                # increase pointer by one.
                if input[pointer:pointer+1] == u'.' and numbers_seen < 4:
                    pointer += 1
                # 2. Otherwise, validation error, return failure.
                else:
                    validation_error_flag.set()
                    return Failure
            # 3. If c is not an ASCII digit, validation error, return failure.
            if not ASCII_DIGIT_RE.match(input[pointer:pointer+1]):
                validation_error_flag.set()
                return Failure
            # 4. While c is an ASCII digit, run these subsubsteps:
            while ASCII_DIGIT_RE.match(input[pointer:pointer+1]):
                # 1. Let number be c interpreted as decimal number.
                number = int(input[pointer:pointer+1])
                # 2. If value is null, set value to number.
                if value is None:
                    value = number
                # Otherwise, if value is 0, validation error, return failure.
                elif value == 0:
                    validation_error_flag.set()
                    return Failure
                # Otherwise, set value to value × 10 + number.
                else:
                    value = value * 10 + number
                # 3. Increase pointer by one.
                pointer += 1
                # 4. If value is greater than 255, validation error, return failure.
                if value > 255:
                    validation_error_flag.set()
                    return Failure
            # 5. Set piece to piece × 0x100 + value.
            address.pieces[piece_pointer] = address.pieces[piece_pointer] * 0x100 + value
            # 6. Increase numbersSeen by one.
            numbers_seen +=  1
            # 7. If numbersSeen is 2 or 4, then increase piece pointer by one.
            if numbers_seen == 2 or numbers_seen == 4:
                piece_pointer += 1
            # 8. If c is the EOF code point and numbersSeen is not 4,
            # validation error, return failure.
            if input[pointer:pointer+1] == u'' and numbers_seen != 4:
                validation_error_flag.set()
                return Failure
    # 11. Finale: If compress pointer is non-null, run these substeps:
    if compress_pointer is not None:
        # 1. Let swaps be piece pointer − compress pointer.
        swaps = piece_pointer - compress_pointer
        # 2. Set piece pointer to seven.
        piece_pointer = 7
        # 3. While piece pointer is not zero and swaps is greater than zero,
        # swap piece with the piece at pointer compress pointer + swaps − 1,
        # and then decrease both piece pointer and swaps by one.
        while piece_pointer != 0 and swaps > 0:
            tmp = address.pieces[piece_pointer]
            address.pieces[piece_pointer] = address.pieces[compress_pointer + swaps - 1]
            address.pieces[compress_pointer + swaps - 1] = tmp
            piece_pointer -= 1
            swaps -= 1
    # 12. Otherwise, if compress pointer is null and piece pointer is not
    # eight, validation error, return failure.
    elif compress_pointer is None and piece_pointer != 8:
        validation_error_flag.set()
        return Failure
    # 13. Return address.
    return address

def parse_ipv4_number(input, validation_error_flag):
    # XXX https://github.com/whatwg/url/issues/167
    # I reversed steps 3 and 4 to fix this

    # The IPv4 number parser takes a string input and a syntaxViolationFlag
    # pointer, and then runs these steps:
    # 1. Let R be 10.
    r = 10
    # 2. If input contains at least two code points and the first two code
    # points are either "0x" or "0X", run these substeps:
    if input[:2] in (u'0x', u'0X'):
        # 1. Set syntaxViolationFlag.
        validation_error_flag.set()
        # 2. Remove the first two code points from input.
        input = input[2:]
        # 3. Set R to 16.
        r = 16
    # 4. Otherwise, if input contains at least two code points and the first
    # code point is "0", run these substeps:
    elif len(input) >= 2 and input[:1] == u'0':
        # 1. Set syntaxViolationFlag.
        validation_error_flag.set()
        # 2. Remove the first code point from input.
        input = input[1:]
        # 3. Set R to 8.
        r = 8
    # 3. If input is the empty string, return zero.
    if input == u'':
        return 0
    # 5. If input contains a code point that is not a radix-R digit, and return
    # failure.
    # 6. Return the mathematical integer value that is represented by input in
    # radix-R notation, using ASCII hex digits for digits with values 0 through
    # 15.
    try:
        return int(input, r)
    except ValueError:
        return Failure

def parse_ipv4(input):
    # 1. Let syntaxViolationFlag be unset.
    validation_error_flag = ValidationErrorFlag()
    # 2. Let parts be input split on ".".
    parts = input.split(u'.')
    # 3. If the last item in parts is the empty string, set syntaxViolationFlag
    # and remove the last item from parts.
    # XXX see https://github.com/whatwg/url/issues/79
    if parts[-1] == u'':
        validation_error_flag.set()
        if len(parts) > 1:
            parts.pop()
    # 4. If parts has more than four items, return input.
    if len(parts) > 4:
        return input
    # 5. Let numbers be the empty list.
    numbers = []
    # 6. For each part in parts:
    for part in parts:
        # 1. If part is the empty string, return input.
        # Example: 0..0x300 is a domain, not an IPv4 address.
        if part == u'':
            return input
        # 2. Let n be the result of parsing part using syntaxViolationFlag.
        n = parse_ipv4_number(part, validation_error_flag)
        # 3. If n is failure, return input.
        if n == Failure:
            return input
        # 4. Append n to numbers.
        numbers.append(n)
    # 7. If syntaxViolationFlag is set, syntax violation.
    if validation_error_flag.is_set():
        # XXX syntax violation
        pass
    # 8. If any item in numbers is greater than 255, syntax violation.
    if any(n > 255 for n in numbers):
        # XXX syntax violation
        pass
    # 9. If any but the last item in numbers is greater than 255, return
    # failure.
    if any(n > 255 for n in numbers[:-1]):
        return Failure
    # 10. If the last item in numbers is greater than or equal to
    # 256**(5 − the number of items in numbers), syntax violation, return
    # failure.
    if numbers and numbers[-1] >= 256**(5 - len(numbers)):
        # XXX syntax violation
        return Failure
    # 11. Let ipv4 be the last item in numbers.
    ipv4 = numbers[-1]
    # 12. Remove the last item from numbers.
    numbers.pop()
    # 13. Let counter be zero.
    counter = 0
    # 14. For each n in numbers:
    for n in numbers:
        # 1. Increment ipv4 by n × 256(3 − counter).
        ipv4 += n * 256**(3 - counter)
        # 2. Increment counter by one.
        counter += 1
    return ipv4

def parse_host(input, flag_unicode=False):
    '''
    XXX should it returns tuple (parsed_host, validation_error) where
    parsed_host may be Failure.
    '''
    # 1. If input starts with "[", run these substeps:
    if input[:1] == u'[':
        # 1. If input does not end with "]", syntax violation, return failure.
        if input[-1:] != u']':
            # XXX syntax violation
            return Failure
        # 2. Return the result of IPv6 parsing input with its leading "[" and
        # trailing "]" removed.
        validation_error_flag = ValidationErrorFlag()
        return parse_ipv6(input[1:-1], validation_error_flag)
    # 2. Let domain be the result of UTF-8 decode without BOM on the percent
    # decoding of UTF-8 encode on input.
    domain = pct_decode(input.encode('utf-8')).decode('utf-8')
    # 3. Let asciiDomain be the result of running domain to ASCII on domain.
    try:
        ascii_domain = idna.encode(
                domain, uts46=True, transitional=True).decode('ascii')
    except Exception as e:
        if isinstance(e, idna.IDNAError):
            if e.args[0] == 'Empty domain':
                # XXX we do this because VerifyDnsLength=false
                # how else does the idna library differ from the spec?
                ascii_domain = domain
            else:
                try:
                    ascii_domain = domain.encode('idna').decode('ascii')
                except Exception as e:
                    # 4. If asciiDomain is failure, return failure.
                    # XXX syntax violation
                    return Failure
        else:
            # 4. If asciiDomain is failure, return failure.
            # XXX syntax violation
            return Failure
    # 5. If asciiDomain contains U+0000, U+0009, U+000A, U+000D, U+0020, "#",
    # "%", "/", ":", "?", "@", "[", "\", or "]", syntax violation, return
    # failure.
    if any(c in ascii_domain for c in u'\0\x09\x0a\x0d\x20#%/:?@[\\]'):
        # XXX syntax violation
        return Failure
    # 6. Let ipv4Host be the result of IPv4 parsing asciiDomain.
    ipv4_host = parse_ipv4(ascii_domain)
    # 7. If ipv4Host is an IPv4 address or failure, return ipv4Host.
    if isinstance(ipv4_host, int) or ipv4_host == Failure:
        return ipv4_host
    # 8. Return asciiDomain if the Unicode flag is unset, and the result of
    # running domain to Unicode on asciiDomain otherwise.
    if flag_unicode:
        return idna.decode(ascii_domain.decode('ascii'))
    else:
        return ascii_domain

class BasicParseStateMachine:
    def __init__(
            self, input, base=None, encoding_override=None, url=None,
            state_override=None):
        self.input = input
        self.url = url
        self.base = base
        self.encoding_override = encoding_override
        self.url = url
        self.state_override = state_override
        self.validation_error = False

    def __repr__(self):
        return str(vars(self))

    def scheme_start_state(self):
        c = self.input[self.pointer:self.pointer+1]
        # 1. If c is an ASCII alpha, append c, lowercased, to buffer, and set
        # state to scheme state.
        if ASCII_ALPHA_RE.match(c):
            self.buffer += c.lower()
            self.state = self.scheme_state
        # 2. Otherwise, if state override is not given, set state to no scheme
        # state, and decrease pointer by one.
        elif not self.state_override:
            self.state = self.no_scheme_state
            self.pointer -= 1
        # 3. Otherwise, syntax violation, terminate this algorithm.
        else:
            self.validation_error = True
            raise TerminateAlgorithm

    def scheme_state(self):
        c = self.input[self.pointer:self.pointer+1]
        # 1. If c is an ASCII alphanumeric, "+", "-", or ".", append c,
        # lowercased, to buffer.
        if ASCII_ALPHANUMERIC_RE.match(c) or c == u'+' or c == u'-' or c == '.':
            self.buffer += c.lower()
        # 2. Otherwise, if c is ":", run these substeps:
        elif c == u':':
            # 1. If state override is given, run these subsubsteps:
            if self.state_override:
                # 1. If url’s scheme is a special scheme and buffer is not,
                # terminate this algorithm.
                # 2. If url’s scheme is not a special scheme and buffer is,
                # terminate this algorithm.
                if ((self.url.scheme in SPECIAL_SCHEMES
                    and not self.buffer in SPECIAL_SCHEMES)
                    or (not self.url.scheme in SPECIAL_SCHEMES
                        and self.buffer in SPECIAL_SCHEMES)):
                    raise TerminateAlgorithm
            # 2. Set url’s scheme to buffer.
            self.url.scheme = unicode(self.buffer)
            # 3. Set buffer to the empty string.
            self.buffer = u''
            # 4. If state override is given, terminate this algorithm.
            if self.state_override:
                raise TerminateAlgorithm
            # 5. If url’s scheme is "file", run these subsubsteps:
            if self.url.scheme == u'file':
                # 1. If remaining does not start with "//", syntax violation.
                if self.remaining(2) != u'//':
                    self.validation_error = True
                # 2. Set state to file state.
                self.state = self.file_state
            # 6. Otherwise, if url is special, base is non-null, and base’s
            # scheme is equal to url’s scheme, set state to special relative or
            # authority state.
            # Note: This means that base’s cannot-be-a-base-URL flag is unset.
            elif (self.url.is_special() and self.base
                    and self.base.scheme == self.url.scheme):
                self.state = self.special_relative_or_authority_state
            # 7. Otherwise, if url is special, set state to special authority
            # slashes state.
            elif self.url.is_special():
                self.state = self.special_authority_slashes_state
            # 8. Otherwise, if remaining starts with an "/", set state to path
            # or authority state, and increase pointer by one.
            elif self.remaining(1) == u'/':
                self.state = self.path_or_authority_state
                self.pointer += 1
            # 9. Otherwise, set url’s cannot-be-a-base-URL flag, append an
            # empty string to url’s path, and set state to cannot-be-a-base-URL
            # path state.
            else:
                self.url.cannot_be_a_base_url = True
                self.url.path.append(u'')
                self.state = self.cannot_be_a_base_url_path_state
        # 3. Otherwise, if state override is not given, set buffer to the empty
        # string, state to no scheme state, and start over (from the first code
        # point in input).
        elif not self.state_override:
            self.buffer = u''
            self.state = self.no_scheme_state
            self.pointer = -1
        # 4. Otherwise, syntax violation, terminate this algorithm.
        else:
            self.validation_error = True
            raise TerminateAlgorithm

    def no_scheme_state(self):
        c = self.input[self.pointer:self.pointer+1]

        # 1. If base is null, or base’s cannot-be-a-base-URL flag is set and c
        # is not "#", syntax violation, return failure.
        if not self.base or (self.base.cannot_be_a_base_url and c != u'#'):
            self.validation_error
            return Failure
        # 2. Otherwise, if base’s cannot-be-a-base-URL flag is set and c is
        # "#", set url’s scheme to base’s scheme, url’s path to base’s path,
        # url’s query to base’s query, url’s fragment to the empty string, set
        # url’s cannot-be-a-base-URL flag, and set state to fragment state.
        elif self.base.cannot_be_a_base_url and c == u'#':
            self.url.scheme = self.base.scheme
            self.url.path = self.base.path
            self.url.query = self.base.query
            self.url.fragment = u''
            self.url.cannot_be_a_base_url = True
            self.state = self.fragment_state
        # 3. Otherwise, if base’s scheme is not "file", set state to relative
        # state and decrease pointer by one.
        elif self.base.scheme != u'file':
            self.state = self.relative_state
            self.pointer -= 1
        # 4. Otherwise, set state to file state and decrease pointer by one.
        else:
            self.state = self.file_state
            self.pointer -= 1

    def special_relative_or_authority_state(self):
        c = self.input[self.pointer:self.pointer+1]

        # If c is "/" and remaining starts with "/", set state to special
        # authority ignore slashes state and increase pointer by one.
        if c == u'/' and self.remaining(1) == u'/':
            self.state = self.special_authority_ignore_slashes_state
            self.pointer += 1
        # Otherwise, syntax violation, set state to relative state and decrease
        # pointer by one.
        else:
            self.validation_error = True
            self.state = self.relative_state
            self.pointer -= 1

    def path_or_authority_state(self):
        c = self.input[self.pointer:self.pointer+1]
        # If c is "/", set state to authority state.
        if c == u'/':
            self.state = self.authority_state
        # Otherwise, set state to path state, and decrease pointer by one.
        else:
            self.state = self.path_state
            self.pointer -= 1

    def relative_state(self):
        c = self.input[self.pointer:self.pointer+1]

        # Set url’s scheme to base’s scheme, and then, switching on c:
        self.url.scheme = self.base.scheme
        # ↪ EOF code point
        #   Set url’s username to base’s username, url’s password to base’s
        #   password, url’s host to base’s host, url’s port to base’s port,
        #   url’s path to base’s path, and url’s query to base’s query.
        if c == u'':
            self.url.username = self.base.username
            self.url.password = self.base.password
            self.url.host = self.base.host
            self.url.port = self.base.port
            self.url.path = self.base.path
            self.url.query = self.base.query
        # ↪ "/"
        #   Set state to relative slash state.
        elif c == u'/':
            self.state = self.relative_slash_state
        # ↪ "?"
        #   Set url’s username to base’s username, url’s password to base’s
        #   password, url’s host to base’s host, url’s port to base’s port,
        #   url’s path to base’s path, url’s query to the empty string, and
        #   state to query state.
        elif c == u'?':
            self.url.username = self.base.username
            self.url.password = self.base.password
            self.url.host = self.base.host
            self.url.port = self.base.port
            self.url.path = self.base.path
            self.url.query = u''
            self.state = self.query_state
        # ↪ "#"
        #   Set url’s username to base’s username, url’s password to base’s
        #   password, url’s host to base’s host, url’s port to base’s port,
        #   url’s path to base’s path, url’s query to base’s query, url’s
        #   fragment to the empty string, and state to fragment state.
        elif c == u'#':
            self.url.username = self.base.username
            self.url.password = self.base.password
            self.url.host = self.base.host
            self.url.port = self.base.port
            self.url.path = self.base.path
            self.url.query = self.base.query
            self.url.fragment = u''
            self.state = self.fragment_state
        # ↪ Otherwise
        else:
            # If url is special and c is "\", syntax violation, set state to
            # relative slash state.
            if self.url.is_special() and c == u'\\':
                self.validation_error = True
                self.state = self.relative_slash_state
            # Otherwise, run these steps:
            else:
                # 1. Set url’s username to base’s username, url’s password to
                # base’s password, url’s host to base’s host, url’s port to
                # base’s port, url’s path to base’s path, and then remove url’s
                # path’s last entry, if any.
                self.url.username = self.base.username
                self.url.password = self.base.password
                self.url.host = self.base.host
                self.url.port = self.base.port
                self.url.path = self.base.path
                if self.url.path:
                    self.url.path.pop()
                # 2. Set state to path state, and decrease pointer by one.
                self.state = self.path_state
                self.pointer -= 1

    def relative_slash_state(self):
        c = self.input[self.pointer:self.pointer+1]
        # 1. If either c is "/", or url is special and c is "\", run these
        # substeps:
        if c == u'/' or self.url.is_special() and c == u'\\':
            # 1. If c is "\", syntax violation.
            if c == u'\\':
                self.validation_error = True
            # 2. Set state to special authority ignore slashes state.
            self.state = self.special_authority_ignore_slashes_state
        # 2. Otherwise, set url’s username to base’s username, url’s password
        # to base’s password, url’s host to base’s host, url’s port to base’s
        # port, state to path state, and then, decrease pointer by one.
        else:
            self.url.username = self.base.username
            self.url.password = self.base.password
            self.url.host = self.base.host
            self.url.port = self.base.port
            self.state = self.path_state
            self.pointer -= 1

    def special_authority_slashes_state(self):
        c = self.input[self.pointer:self.pointer+1]
        # If c is "/" and remaining starts with "/", set state to special
        # authority ignore slashes state, and increase pointer by one.
        if c == u'/' and self.remaining(1) == u'/':
            self.state = self.special_authority_ignore_slashes_state
            self.pointer += 1
        # Otherwise, syntax violation, set state to special authority ignore
        # slashes state, and decrease pointer by one.
        else:
            self.validation_error = True
            self.state = self.special_authority_ignore_slashes_state
            self.pointer -= 1

    def special_authority_ignore_slashes_state(self):
        c = self.input[self.pointer:self.pointer+1]
        # If c is neither "/" nor "\", set state to authority state, and
        # decrease pointer by one.
        if c != u'/' and c != u'\\':
            self.state = self.authority_state
            self.pointer -= 1
        # Otherwise, syntax violation.
        else:
            self.validation_error = True

    def authority_state(self):
        c = self.input[self.pointer:self.pointer+1]
        # 1. If c is "@", run these substeps:
        if c == u'@':
            # 1. Syntax violation.
            self.validation_error = True
            # 2. If the @ flag is set, prepend "%40" to buffer.
            if self.flag_at:
                self.buffer = u'%40' + self.buffer
            # 3. Set the @ flag.
            self.flag_at = True
            # 4. For each codePoint in buffer, run these substeps:
            for i in range(len(self.buffer)):
                codepoint = self.buffer[i:i+1]
                # 1. If codePoint is ":" and url’s password is null, set url’s
                # password to the empty string and run these substeps for the
                # next code point.
                if codepoint == u':' and self.url.password is None:
                    self.url.password = u''
                    continue
                # 2. Let encodedCodePoints be the result of running UTF-8
                # percent encode codePoint using the userinfo encode set.
                encoded = utf8_pct_encode(codepoint, USERINFO_ENCODE_SET_RE)
                # 3. If url’s password is non-null, append encodedCodePoints to
                # url’s password.
                if self.url.password is not None:
                    self.url.password = self.url.password + encoded
                # 4. Otherwise, append encodedCodePoints to url’s username.
                else:
                    self.url.username += encoded
            # 5. Set buffer to the empty string.
            self.buffer = u''
        # 2. Otherwise, if one of the following is true
        # - c is EOF code point, "/", "?", or "#"
        # - url is special and c is "\"
        # then decrease pointer by the number of code points in buffer plus
        # one, set buffer to the empty string, and set state to host state.
        elif c == u'' or c == u'/' or c == u'?' or c == u'#' or (
                self.url.is_special() and c == u'\\'):
            self.pointer -= len(self.buffer) + 1
            self.buffer = u''
            self.state = self.host_state
        # 3. Otherwise, append c to buffer.
        else:
            self.buffer += c

    def hostname_state(self):
        c = self.input[self.pointer:self.pointer+1]
        # 1. If c is ":" and the [] flag is unset, run these substeps:
        if c == u':' and not self.flag_brackets:
            # 1. If url is special and buffer is the empty string, return
            # failure.
            if self.url.is_special() and self.buffer == u'':
                return Failure
            # 2. Let host be the result of host parsing buffer.
            host = parse_host(self.buffer)
            # 3. If host is failure, return failure.
            if host == Failure:
                return Failure
            # 4. Set url’s host to host, buffer to the empty string, and state
            # to port state.
            self.url.host = host
            self.buffer = u''
            self.state = self.port_state
            # 5. If state override is hostname state, terminate this algorithm.
            if self.state_override == self.hostname_state:
                raise TerminateAlgorithm
        # 2. Otherwise, if one of the following is true
        # - c is EOF code point, "/", "?", or "#"
        # - url is special and c is "\"
        # then decrease pointer by one, and run these substeps:
        elif c == u'' or c == u'/' or c == u'?' or c == u'#' or (
                self.url.is_special() and c == u'\\'):
            self.pointer -= 1
            # 1. If url is special and buffer is the empty string, return
            # failure.
            if self.url.is_special() and self.buffer == u'':
                return Failure
            # 2. Let host be the result of host parsing buffer.
            host = parse_host(self.buffer)
            # 3. If host is failure, return failure.
            if host == Failure:
                return Failure
            # 4. Set url’s host to host, buffer to the empty string, and state
            # to path start state.
            self.url.host = host
            self.buffer = u''
            self.state = self.path_start_state
            # 5. If state override is given, terminate this algorithm.
            if self.state_override:
                raise TerminateAlgorithm
        # 3. Otherwise, run these substeps:
        else:
            # 1. If c is "[", set the [] flag.
            if c == u'[':
                self.flag_brackets = True
            # 2. If c is "]", unset the [] flag.
            if c == u']':
                self.flag_brackets = False
            # 3. Append c to buffer.
            self.buffer += c

    host_state = hostname_state

    def remaining(self, length=None):
        if length is not None:
            return self.input[self.pointer+1:self.pointer+1+length]
        else:
            return self.input[self.pointer+1:]

    def port_state(self):
        c = self.input[self.pointer:self.pointer+1]
        # 1. If c is an ASCII digit, append c to buffer.
        if ASCII_DIGIT_RE.match(c):
            self.buffer += c
        # 2. Otherwise, if one of the following is true
        # - c is EOF code point, "/", "?", or "#"
        # - url is special and c is "\"
        # - state override is given
        elif c == u'' or c == u'/' or c == u'?' or c == u'#' or (
                self.url.is_special() and c == u'\\') or self.state_override:
            # run these substeps:
            # 1. If buffer is not the empty string, run these subsubsteps:
            if self.buffer != u'':
                # 1. Let port be the mathematical integer value that is
                # represented by buffer in radix-10 using ASCII digits for
                # digits with values 0 through 9.
                port = int(self.buffer)
                # 2. If port is greater than 2**16 − 1, syntax violation,
                # return failure.
                if port > 2**16 - 1:
                    self.validation_error = True
                    return Failure
                # 3. Set url’s port to null, if port is url’s scheme’s default
                # port, and to port otherwise.
                if port == SPECIAL_SCHEMES.get(self.url.scheme):
                    self.url.port = None
                else:
                    self.url.port = port
                # 4. Set buffer to the empty string.
                self.buffer = u''
            # 2. If state override is given, terminate this algorithm.
            elif self.state_override:
                raise TerminateAlgorithm
            # 3. Set state to path start state, and decrease pointer by one.
            self.state = self.path_start_state
        # 3. Otherwise, syntax violation, return failure.
        else:
            self.validation_error = True
            return Failure

    def file_state(self):
        c = self.input[self.pointer:self.pointer+1]
        # 1. Set url’s scheme to "file".
        self.url.scheme = u'file'
        # 2. If c is "/" or "\", then:
        if c in (u'/', u'\\'):
            # 1. If c is "\", validation error.
            if c == u'\\':
                self.validation_error = True
            # 2. Set state to file slash state.
            self.state = self.file_slash_state

        # 3. Otherwise, if base is non-null and base’s scheme is "file", switch
        # on c:
        elif self.base and self.base.scheme == 'file':
            # ↪ EOF code point
            if c == u'':
                # Set url’s host to base’s host, url’s path to a copy of base’s
                # path, and url’s query to base’s query.
                self.url.host = self.base.host
                self.url.path = list(self.base.path)
                self.url.query = self.base.query
            # ↪ "?"
            elif c == u'?':
                # Set url’s host to base’s host, url’s path to a copy of base’s
                # path, url’s query to the empty string, and state to query
                # state.
                self.url.host = self.base.host
                self.url.path = list(self.base.path)
                self.url.query = u''
                self.state = self.query_state
            # ↪ "#"
            elif c == u'#':
                # Set url’s host to base’s host, url’s path to a copy of base’s
                # path, url’s query to base’s query, url’s fragment to the
                # empty string, and state to fragment state.
                self.url.host = self.base.host
                self.url.path = list(self.base.path)
                self.url.query = self.base.query
                self.url.fragment = u''
                self.state = self.fragment_state
            # ↪ Otherwise
            else:
                # 1. If at least one of the following is true
                # - c and the first code point of remaining are not a Windows
                # drive letter
                # - remaining consists of one code point
                # - remaining’s second code point is not "/", "\", "?", or "#"
                # then set url’s host to base’s host, url’s path to a copy of
                # base’s path, and then shorten url’s path.
                # Note: This is a (platform-independent) Windows drive letter
                # quirk.
                if (self.base and self.base.scheme == u'file' and (
                        not is_windows_drive_letter(c + self.remaining(1))
                        or self.pointer + 1 == len(self.buffer)
                        or self.remaining(2)[1:2] not in (
                            u'/', u'\\', u'?', u'#'))):
                    self.url.host = self.base.host
                    self.url.path = self.base.path
                    self.url.shorten_path()
                # 2. Otherwise, validation error
                else:
                    validation_error = True
                # 3. Set state to path state, and decrease pointer by one.
                self.state = self.path_state
                self.pointer -= 1
        # 4. Otherwise, set state to path state, and decrease pointer by one.
        else:
            self.state = self.path_state
            self.pointer -= 1

    def file_slash_state(self):
        c = self.input[self.pointer:self.pointer+1]
        # 1. If c is "/" or "\", run these substeps:
        if c == u'/' or c == u'\\':
            # 1. If c is "\", syntax violation.
            if c == u'\\':
                self.validation_error = True
            # 2. Set state to file host state.
            self.state = self.file_host_state
        # 2. Otherwise, run these substeps:
        else:
            # 1. If base is non-null, base’s scheme is "file", and base’s path
            # first string is a normalized Windows drive letter, append base’s
            # path first string to url’s path.
            # Note: This is a (platform-independent) Windows drive letter
            # quirk. Both url’s and base’s host are null under these conditions
            # and therefore not copied.
            if (self.base and self.base.scheme == u'file' and self.base.path
                    and is_normalized_windows_drive_letter(self.base.path[0])):
                self.url.path.append(self.base.path[0])
            # 2. Set state to path state, and decrease pointer by one.
            self.state = self.path_state
            self.pointer -= 1

    def file_host_state(self):
        c = self.input[self.pointer:self.pointer+1]
        # 1. If c is EOF code point, "/", "\", "?", or "#", decrease pointer by
        # one, and run these substeps:
        if c == u'' or c == u'/' or c == u'\\' or c == u'?' or c == u'#':
            self.pointer -= 1
            # 1. If buffer is a Windows drive letter, syntax violation, set
            # state to path state.
            # Note: This is a (platform-independent) Windows drive letter
            # quirk. buffer is not reset here and instead used in the path
            # state.
            if is_windows_drive_letter(self.buffer):
                self.validation_error = True
                self.state = self.path_state
            # 2. Otherwise, if buffer is the empty string, set state to path
            # start state.
            elif self.buffer == u'':
                self.state = self.path_start_state
            # 3. Otherwise, run these steps:
            else:
                # 1. Let host be the result of host parsing buffer.
                host = parse_host(self.buffer)
                # 2. If host is failure, return failure.
                if host == Failure:
                    return Failure
                if host != u'localhost':
                    self.url.host = host
                self.buffer = u''
                self.state = self.path_start_state
        # 2. Otherwise, append c to buffer.
        else:
            self.buffer += c

    def path_start_state(self):
        c = self.input[self.pointer:self.pointer+1]
        # 1. If url is special and c is "\", syntax violation.
        if self.url.is_special() and c == u'\\':
            self.validation_error = True
        # 2. Set state to path state, and if neither c is "/", nor url is
        # special and c is "\", decrease pointer by one.
        self.state = self.path_state
        if c != u'/' and not (self.url.is_special() and c == u'\\'):
            self.pointer -= 1

    def path_state(self):
        c = self.input[self.pointer:self.pointer+1]
        # 1. If one of the following is true
        # - c is EOF code point or "/"
        # - url is special and c is "\"
        # - state override is not given and c is "?" or "#"
        # then run these substeps:
        if c == u'' or c == u'/' or (self.url.is_special() and c == u'\\') or (
                not self.state_override and c in u'?#'):
            # 1. If url is special and c is "\", syntax violation.
            if self.url.is_special() and c == u'\\':
                self.validation_error = True
            # 2. If buffer is a double-dot path segment, shorten url’s path,
            # and then if neither c is "/", nor url is special and c is "\",
            # append the empty string to url’s path.
            if is_double_dot_path_segment(self.buffer):
                self.url.shorten_path()
                if c != u'/' and not (self.url.is_special() and c == u'\\'):
                    self.url.path.append(u'')
            # 3. Otherwise, if buffer is a single-dot path segment and if
            # neither c is "/", nor url is special and c is "\", append the
            # empty string to url’s path.
            elif is_single_dot_path_segment(self.buffer) and c != u'/' and not (
                    self.url.is_special() and c == u'\\'):
                self.url.path.append(u'')
            # 4. Otherwise, if buffer is not a single-dot path segment, run
            # these subsubsteps:
            elif not is_single_dot_path_segment(self.buffer):
                # 1. If url’s scheme is "file", url’s path is empty, and buffer
                # is a Windows drive letter, run these subsubsubsteps:
                if (self.url.scheme == u'file' and not self.url.path
                        and is_windows_drive_letter(self.buffer)):
                    # 1. If url’s host is non-null, syntax violation.
                    if self.url.host:
                        self.validation_error = True
                    # 2. Set url’s host to null and replace the second code
                    # point in buffer with ":".
                    # Note: This is a (platform-independent) Windows drive
                    # letter quirk.
                    self.url.host = None
                    self.buffer = self.buffer[0] + u':' + self.buffer[2:]
                # 2. Append buffer to url’s path.
                self.url.path.append(self.buffer)
            # 5. Set buffer to the empty string.
            self.buffer = u''
            # 6. If c is "?", set url’s query to the empty string, and state to
            # query state.
            if c == u'?':
                self.url.query = u''
                self.state = self.query_state
            # 7. If c is "#", set url’s fragment to the empty string, and state
            # to fragment state.
            if c == u'#':
                self.url.fragment = u''
                self.state = self.fragment_state
        # 2. Otherwise, run these steps:
        else:
            # 1. If c is not a URL code point and not "%", syntax violation.
            if c != u'%' and not is_url_codepoint(c):
                self.validation_error = True
            # 2. If c is "%" and remaining does not start with two ASCII hex
            # digits, syntax violation.
            if c == u'%' and not (
                    ASCII_HEX_DIGIT_RE.match(self.remaining(1))
                    and ASCII_HEX_DIGIT_RE.match(self.remaining(2)[1:])):
                self.validation_error = True
            # 3. If c is "%" and remaining, ASCII lowercased starts with "2e",
            # append "." to buffer and increase pointer by two.
            if c == u'%' and self.remaining(2).lower() == u'2e':
                self.buffer += u'.'
                self.pointer += 2
            # 4. Otherwise, UTF-8 percent encode c using the default encode
            # set, and append the result to buffer.
            else:
                self.buffer += utf8_pct_encode(c)

    def cannot_be_a_base_url_path_state(self):
        c = self.input[self.pointer:self.pointer+1]
        # 1. If c is "?", set url’s query to the empty string and state to
        # query state.
        if c == u'?':
            self.url.query = u''
            self.state = self.query_state
        # 2. Otherwise, if c is "#", set url’s fragment to the empty string and
        # state to fragment state.
        elif c == u'#':
            self.url.fragment = u''
            self.state = self.fragment_state
        # 3. Otherwise, run these substeps:
        else:
            # 1. If c is not EOF code point, not a URL code point, and not "%",
            # syntax violation.
            if c != u'' and c != u'%' and not is_url_codepoint(c):
                self.validation_error = True
            # 2. If c is "%" and remaining does not start with two ASCII hex
            # digits, syntax violation.
            if c == u'%' and not (
                    ASCII_HEX_DIGIT_RE.match(self.remaining(1))
                    and ASCII_HEX_DIGIT_RE.match(self.remaining(2)[1:])):
                self.validation_error = True
            # 3. If c is not EOF code point, UTF-8 percent encode c using the
            # simple encode set, and append the result to the first string in
            # url’s path.
            if c != u'':
                self.url.path[0] += utf8_pct_encode(c, C0_CONTROL_ENCODE_SET)

    def query_state(self):
        c = self.input[self.pointer:self.pointer+1]
        # 1. If c is EOF code point, or state override is not given and c is
        # "#", run these substeps:
        if c == u'' or not self.state_override and c == u'#':
            # 1. If url is not special or url’s scheme is either "ws" or "wss",
            # set encoding to UTF-8.
            if not self.url.is_special() or self.url.scheme in (u'ws', u'wss'):
                self.encoding = 'utf-8'
            # 2. Set buffer to the result of encoding buffer using encoding.
            self.buffer = self.buffer.encode(self.encoding)
            # 3. For each byte in buffer run these subsubsteps:
            for i in range(len(self.buffer)):
                byte = ord(self.buffer[i:i+1])
                # 1. If byte is less than 0x21, greater than 0x7E, or is 0x22,
                # 0x23, 0x3C, or 0x3E, append byte, percent encoded, to url’s
                # query.
                if byte < 0x21 or byte > 0x7e or byte in (
                        0x22, 0x23, 0x3c, 0x3e):
                    self.url.query += u'%%%02X' % byte
                # 2. Otherwise, append a code point whose value is byte to
                # url’s query.
                else:
                    self.url.query += chr(byte)
            # 4. Set buffer to the empty string.
            self.buffer = u''
            # 5. If c is "#", set url’s fragment to the empty string, and state
            # to fragment state.
            if c == u'#':
                self.url.fragment = u''
                self.state = self.fragment_state
        # 2. Otherwise, run these substeps:
        else:
            # 1. If c is not a URL code point and not "%", syntax violation.
            if c != u'%' and not is_url_codepoint(c):
                self.validation_error = True
            # 2. If c is "%" and remaining does not start with two ASCII hex
            # digits, syntax violation.
            if c == u'%' and not (
                    ASCII_HEX_DIGIT_RE.match(self.remaining(1))
                    and ASCII_HEX_DIGIT_RE.match(self.remaining(2)[1:])):
                self.validation_error = True
            # 3. Append c to buffer.
            self.buffer += c

    def fragment_state(self):
        c = self.input[self.pointer:self.pointer+1]
        # Switching on c:
        # ↪ EOF code point
        #   Do nothing.
        if c == u'':
            pass
        # ↪ U+0000
        #   Syntax violation.
        elif c == u'\0':
            self.validation_error = True
        else:
            # 1. If c is not a URL code point and not "%", syntax violation.
            if c != u'%' and not is_url_codepoint(c):
                self.validation_error = True
            # 2. If c is "%" and remaining does not start with two ASCII hex
            # digits, syntax violation.
            if c == u'%' and not (
                    ASCII_HEX_DIGIT_RE.match(self.remaining(1))
                    and ASCII_HEX_DIGIT_RE.match(self.remaining(2)[1:])):
                self.validation_error = True
            ### # 3. Append c to url’s fragment.
            ### # Note: Unfortunately not using percent-encoding is intentional as
            ### # implementations with majority market share exhibit this behavior.
            ### self.url.fragment += c
            # 3. UTF-8 percent encode c using the C0 control percent-encode set
            # and append the result to url’s fragment.
            self.url.fragment += utf8_pct_encode(c, C0_CONTROL_ENCODE_SET)


def basic_parse(
        input, base=None, encoding_override=None, url=None,
        state_override=None):
    '''Implements "basic URL parser".'''
    state = BasicParseStateMachine(
            input, base, encoding_override, url, state_override)

    # 1. If url is not given:
    if not state.url:
        # 1. Set url to a new URL.
        state.url = URL()
        # 2. If input contains any leading or trailing C0 control or space,
        # syntax violation.
        # 3. Remove any leading and trailing C0 control or space from input.
        m = re.match(u'\\A[\\x00-\\x20]+(.*)\\Z', state.input, re.DOTALL)
        if m:
            state.validation_error = True
            state.input = m.group(1)
        m = re.match('\\A(.*?)[\\x00-\\x20]+\\Z', state.input, re.DOTALL)
        if m:
            state.validation_error = True
            state.input = m.group(1)

    # 2. If input contains any ASCII tab or newline, syntax violation.
    # 3. Remove all ASCII tab or newline from input.
    tmp = re.sub(u'[\\x09\\x0a\\x0d]', u'', state.input)
    if tmp != state.input:
        validation_error = True
        state.input = tmp

    # 4. Let state be state override if given, or scheme start state
    # otherwise.
    if state_override:
        state.state = state_override
    else:
        state.state = state.scheme_start_state

    # 5. If base is not given, set it to null.
    # 6. Let encoding be UTF-8.
    state.encoding = 'utf-8'

    # 7. If encoding override is given, set encoding to the result of
    # getting an output encoding from encoding override.
    # To get an output encoding from an encoding encoding, run these steps:
    #  1. If encoding is replacement, UTF-16BE, or UTF-16LE, return UTF-8.
    #  2. Return encoding.
    if encoding_override and encoding_override.lower() not in (
            'replacement', 'utf-16', 'utf-16-be', 'utf-16-le'):
        state.encoding = encoding_override

    # 8. Let buffer be the empty string.
    state.buffer = u''

    # 9. Let the @ flag and the [] flag be unset.
    state.flag_at = False
    state.flag_brackets = False

    # 10. Let pointer be a pointer to first code point in input.
    state.pointer = 0

    # 11. Keep running the following state machine by switching on state.
    # If after a run pointer points to EOF code point, go to the next step.
    # Otherwise, increase pointer by one and continue with the state
    # machine.
    while True:
        try:
            result = state.state()
        except TerminateAlgorithm:
            break
        if result == Failure:
            state.url = Failure
            break
        if state.pointer >= len(state.input):
            break
        state.pointer += 1

    # 12. Return url.
    return state.url

def main(args):
    for imput in args[1:]:
        url = basic_parse(imput, base=None)
        print("%s => %s" % (imput, url.serialize()))

if __name__ == '__main__':
    main(sys.argv)
