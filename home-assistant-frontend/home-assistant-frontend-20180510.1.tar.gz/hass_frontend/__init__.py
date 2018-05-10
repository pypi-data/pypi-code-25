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
VERSION = '205d6a8347e71a79bc38789d2cbb8bd7c0acb203'
CREATED_AT = 1525988416
FINGERPRINTS = {
    "config": "9c9f1914250a658c0c77433f75d8f948",
    "dev-event": "7c1f35322b34c176e16f68729b98ae3b",
    "dev-info": "8d3aa9b44db1a4d24212327c547e38c8",
    "dev-mqtt": "84c050acc4975584b7dd88242cea02aa",
    "dev-service": "701e29bd4739269bd8262a6d0406a38e",
    "dev-state": "4978fc7789de9459ba2b0149b107c2b0",
    "dev-template": "bc28e6e7b0ba59cdcd23e248b37622a5",
    "hassio": "421266c5f02dbccd48443907251fa741",
    "history": "e0a69a68d79e2ace6261fd325ee9d780",
    "iframe": "3f237a6addc81215890e8da2454da977",
    "kiosk": "e47111bc9da3c12bc554ef415f6d912b",
    "logbook": "8eb3e8d6e04df43f32b76972ff91d316",
    "mailbox": "aa5f9366332c7c20cd4760adeb60c767",
    "map": "b4f2942c035ae036f79f7a9d2ec2ffcb",
    "shopping-list": "793d9bdb323cb002bfa4e94214940f27"
}
