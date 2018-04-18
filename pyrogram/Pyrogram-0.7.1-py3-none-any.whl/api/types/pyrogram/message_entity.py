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


class MessageEntity(Object):
    """Attributes:
        ID: ``0xb0700004``

    Args:
        type: ``str``
        offset: ``int`` ``32-bit``
        length: ``int`` ``32-bit``
        url (optional): ``str``
        user (optional): :obj:`User <pyrogram.api.types.pyrogram.User>`
    """
    ID = 0xb0700004

    def __init__(self, type, offset, length, url=None, user=None):
        self.type = type  # string
        self.offset = offset  # int
        self.length = length  # int
        self.url = url  # flags.0?string
        self.user = user  # flags.1?User

    @staticmethod
    def read(b: BytesIO, *args) -> "MessageEntity":
        flags = Int.read(b)
        
        type = String.read(b)
        
        offset = Int.read(b)
        
        length = Int.read(b)
        
        url = String.read(b) if flags & (1 << 0) else None
        user = Object.read(b) if flags & (1 << 1) else None
        
        return MessageEntity(type, offset, length, url, user)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.url is not None else 0
        flags |= (1 << 1) if self.user is not None else 0
        b.write(Int(flags))
        
        b.write(String(self.type))
        
        b.write(Int(self.offset))
        
        b.write(Int(self.length))
        
        if self.url is not None:
            b.write(String(self.url))
        
        if self.user is not None:
            b.write(self.user.write())
        
        return b.getvalue()
