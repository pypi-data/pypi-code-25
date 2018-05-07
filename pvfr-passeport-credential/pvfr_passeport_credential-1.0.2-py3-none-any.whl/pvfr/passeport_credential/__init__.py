# Copyright 2018 Jacques Supcik, Passeport vacances Fribourg
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Library for generating verifiable credentials for the Passeport vacances Fribourg

Example:

    This is a short example on how to use this module::

        s_key = bytearray.fromhex("c31e739fbd3acf8592b65a99af8c33ca1e7892f619e8")
        p_key = bytearray.fromhex("ca1414bc18362e57e914f433c6c114326d9ef5acae03")
        c = cred.Credential(s_key, p_key)
        print(c.bar_code(42))
        print(c.serial_pwd(42))

"""

__version__ = "1.0.2"

import hmac
import string
import typing
from hmac import HMAC


class Credential:
    """Main class for all credential based operations

    Note:
        Serial numbers must be between 0 and 9999

    """

    _alphabet = list(set(string.ascii_lowercase + string.digits) - set(list("0Ool19g5SB8qQ")))
    _alphabet.sort()

    def __init__(self, serial_key: bytearray, pwd_key: bytearray):
        self.sKey = serial_key
        self.pKey = pwd_key

    def bar_code(self, no: int) -> str:
        """Generate a verifiable longer serial number that can be used on a bar code

        Args:
            no (int): Short serial number.

        Returns:
            str: The longer verifiable serial number.

        """

        serial: str = "{:04d}".format(no)
        h: HMAC = hmac.new(self.sKey, msg=serial.encode(), digestmod="sha256")
        r: int = int(h.hexdigest(), 16)
        code: str = "{:08d}".format(r)[-8:]
        return code + serial

    def serial_pwd(self, no: int, blocks: int = 3, size: int = 4) -> str:
        """Generate a verifiable password

        The password is an ascii text composed of blocks joined by a hyphen ("-")

        Args:
            no (int): Short serial number.
            blocks (int): Number of blocks in the password.
            size (int): The size of each block.

        Returns:
            str: verifiable password.

        """
        serial: str = "{:04d}".format(no)
        h: HMAC = hmac.new(self.pKey, msg=serial.encode(), digestmod="sha256")
        r: int = int(h.hexdigest(), 16)
        pl: typing.List[str] = list()
        for i in range(blocks):
            p: str = ""
            for j in range(size):
                p += Credential._alphabet[r % len(Credential._alphabet)]
                r = r // len(Credential._alphabet)
            pl.append(p)
        return "-".join(pl)
