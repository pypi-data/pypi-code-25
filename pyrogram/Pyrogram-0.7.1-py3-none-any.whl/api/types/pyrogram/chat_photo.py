# Pyrogram - Telegram MTProto API Client Library for Python
# Copyright (C) 2017-2018 Dan Tès <https://github.com/delivrance>
#
# This file is part of Pyrogram.
#
# Pyrogram is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pyrogram is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from io import BytesIO

from pyrogram.api.core import *


class ChatPhoto(Object):
    """Attributes:
        ID: ``0xb0700015``

    Args:
        small_file_id: ``str``
        big_file_id: ``str``
    """
    ID = 0xb0700015

    def __init__(self, small_file_id, big_file_id):
        self.small_file_id = small_file_id  # string
        self.big_file_id = big_file_id  # string

    @staticmethod
    def read(b: BytesIO, *args) -> "ChatPhoto":
        # No flags
        
        small_file_id = String.read(b)
        
        big_file_id = String.read(b)
        
        return ChatPhoto(small_file_id, big_file_id)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.small_file_id))
        
        b.write(String(self.big_file_id))
        
        return b.getvalue()
