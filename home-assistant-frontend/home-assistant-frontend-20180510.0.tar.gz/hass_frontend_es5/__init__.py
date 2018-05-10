"""Frontend for Home Assistant."""
import os
from user_agents import parse

FAMILY_MIN_VERSION = {
    'Chrome': 54,          # Object.values
    'Chrome Mobile': 54,
    'Firefox': 47,         # Object.values
    'Firefox Mobile': 47,
    'Opera': 41,           # Object.values
    'Edge': 14,            # Array.prototype.includes added in 14
    'Safari': 10,          # Many features not supported by 9
}


def where():
    """Return path to the frontend."""
    return os.path.dirname(__file__)


def version(useragent):
    """Get the version for given user agent."""
    useragent = parse(useragent)

    # on iOS every browser is a Safari which we support from version 11.
    if useragent.os.family == 'iOS':
        # Was >= 10, temp setting it to 12 to work around issue #11387
        return useragent.os.version[0] >= 12

    version = FAMILY_MIN_VERSION.get(useragent.browser.family)
    return version and useragent.browser.version[0] >= version
VERSION = '2a3325efd7efdc25443b2b564f21ffbd400e273a'
CREATED_AT = 1525986428
FINGERPRINTS = {
    "config": "67df8d31d6546019b39986bb68e2c4e4",
    "dev-event": "3dd40fbfd31dc8b4fdf93db6d9416a8a",
    "dev-info": "e46aa410b520a47e8bc39c99fc38a75d",
    "dev-mqtt": "3cfa67605ba0ad5952fd2e8b7689ff73",
    "dev-service": "8e12bc890a0c7bc7586f47b85d4e7aef",
    "dev-state": "2421b60925262932dfa2cb1ec1528025",
    "dev-template": "26531951a6f693713dd7319abf888fae",
    "hassio": "8da5954b26697191398ef269503adc4a",
    "history": "6b66aaf83a1b5d751e4a0fbfaf08d0da",
    "iframe": "856f04c0471478e3b5053a10797e6de4",
    "kiosk": "c36cdcf6ddec9953c6ca21c5f5084a3d",
    "logbook": "6bff139cb7d134f0d8fbb8c4647d8328",
    "mailbox": "97aefc70f69bcb13a0af0a1a6f5968af",
    "map": "27ca1e7182f696058cb235b624abb2b1",
    "shopping-list": "87e02beedd78c96452a0add4c4bb735a"
}
