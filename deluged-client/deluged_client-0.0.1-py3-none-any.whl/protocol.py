
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details
# http://www.gnu.org/licenses/lgpl-3.0.txt

import logging
log = logging.getLogger()

import asyncio
import zlib
import struct
from .rencode import dumps, loads

DELUGE_MAGIC = 68

class Protocol(asyncio.Protocol):
    def __init__(self):
        self._buffer = b''

    def append(self, data):
        self._buffer += data

    def decode(self):
        data = self._buffer
        buflen = len(data)

        if buflen < 5:
            return

        magic = data[0]
        if magic != DELUGE_MAGIC:
            return

        # 'paclen' omits magic 'D'
        paclen = struct.unpack('!i', data[1:5])[0]
        if buflen - 1 < paclen:
            log.debug('Buffer is %s < %s', buflen - 1, paclen)
            return

        try:
            packet = zlib.decompress(data[5:])
            data = loads(packet, decode_utf8=True)
        except zlib.error:
            log.debug('Unable to decode data')
            return

        log.debug(data)
        self._buffer = b''

        return data

    def _send_data(self, data):
        data = dumps(data)
        data = zlib.compress(data)

        header_size = struct.pack('!i', len(data))
        header = b'D' + header_size

        self.transport.write(header)
        self.transport.write(data)

