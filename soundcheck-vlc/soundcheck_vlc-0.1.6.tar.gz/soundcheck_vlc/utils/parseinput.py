import re
from enum import Enum

class ParseStatus(Enum):
    PASS = 0
    PARTIAL_PASS = 1
    FAIL = 2


def parse_hashtag(s):
    """
    Checks if the input string is correctly formatted.
    :param s:
    :return:
    """

    hashtag_re = re.compile(r"(\#)?([\w\-]+)")

    match = hashtag_re.fullmatch(s)
    if match:
        hashtag = match.group(2)
        return ParseStatus.PASS, hashtag
    else:
        match = hashtag_re.match(s)
        if match:
            hashtag = match.group(2)
            return ParseStatus.PARTIAL_PASS, hashtag
        else:
            return ParseStatus.FAIL, None

