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
VERSION = '85c4c51228eda0d623af2ba27dfffe4a2b63d109'
CREATED_AT = 1523974566
FINGERPRINTS = {
    "config": "7b54c8fd3380e141f6c3fda31731e90f",
    "dev-event": "7c1f35322b34c176e16f68729b98ae3b",
    "dev-info": "c7e09aeda0d2fec48fd5cca41403e330",
    "dev-mqtt": "84c050acc4975584b7dd88242cea02aa",
    "dev-service": "701e29bd4739269bd8262a6d0406a38e",
    "dev-state": "4978fc7789de9459ba2b0149b107c2b0",
    "dev-template": "bc28e6e7b0ba59cdcd23e248b37622a5",
    "hassio": "421266c5f02dbccd48443907251fa741",
    "history": "b0ee13e1f75c1ab575024fec02fe1cc4",
    "iframe": "3f237a6addc81215890e8da2454da977",
    "kiosk": "e47111bc9da3c12bc554ef415f6d912b",
    "logbook": "8eb3e8d6e04df43f32b76972ff91d316",
    "mailbox": "aa5f9366332c7c20cd4760adeb60c767",
    "map": "8a86f12afabca7d61a9b44b8fec0ad61",
    "shopping-list": "793d9bdb323cb002bfa4e94214940f27"
}
