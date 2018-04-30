####################################################################################################
#
# sidita - Simple Distributed Task Queue
# Copyright (C) 2018 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

"""Implement a basic message encoder/decoder where the payload can be any pickable Python object.

Message are encoded as a header followed by a pickled payload where the header contains the length
of the pickled payload encoded as a 4-byte unsigned integer.

To decode a message, first read :data:`HEADER_LENGTH` bytes from the stream, then decode the header
to get the next number of bytes to read, finally read them and decode the payload.

"""

####################################################################################################

__all__ = [
    'StandardMessageStream',
    'AsyncMessageStream',
    'HEADER_LENGTH',
    'encode_message',
    'decode_header',
    'decode_message',
]

####################################################################################################

import asyncio
import pickle
import struct

####################################################################################################

HEADER_LENGTH = 4 # permit to pass 4_294_967_295 bytes ~ 4 GB

PROTOCOL = pickle.HIGHEST_PROTOCOL

####################################################################################################

def header_format():

    if HEADER_LENGTH == 4:
        return 'I'
    else:
        raise NotImplementedError

####################################################################################################

def encode_header(payload_length):
    return struct.pack(header_format(), payload_length)

####################################################################################################

def decode_header(header):
    return struct.unpack(header_format(), header)[0]

####################################################################################################

def encode_message(message):

    encoded_message = pickle.dumps(message, protocol=PROTOCOL)
    header = encode_header(len(encoded_message))

    return header + encoded_message

####################################################################################################

def decode_message(pickled_message):
    return pickle.loads(pickled_message)

####################################################################################################

class MessageStream:

    ##############################################

    def __init__(self, input_stream, output_stream):

        self._input = input_stream
        self._output = output_stream

    ##############################################

    def send(self, message):

        self.write(encode_message(message))

    ##############################################

    def receive(self):

        message_length = decode_header(self.read(HEADER_LENGTH))
        return decode_message(self.read(message_length))

    ##############################################

    def write(self, data):
        raise NotImplementedError

    def read(self, length):
        raise NotImplementedError

####################################################################################################

class StandardMessageStream(MessageStream):

    ##############################################

    def __init__(self, input_stream, output_stream):

        self._input = input_stream
        self._output = output_stream

    ##############################################

    def write(self, data):

        self._output.buffer.write(data)
        self._output.flush()

    ##############################################

    def read(self, length):
        return self._input.buffer.read(length)

####################################################################################################

class AsyncMessageStream(MessageStream):

    ##############################################

    def __init__(self, input_stream, output_stream, timeout=None):

        super().__init__(input_stream, output_stream)

        self._timeout = int(timeout)

    ##############################################

    async def receive(self):

        data = await self.read(HEADER_LENGTH)
        message_length = decode_header(data)
        data = await self.read(message_length)
        return decode_message(data)

    ##############################################

    def write(self, data):
        self._input.write(data)

    ##############################################

    async def read(self, length):

        future = self._output.readexactly(length)
        if self._timeout is not None:
            return await asyncio.wait_for(future, self._timeout)
        else:
            return await future
