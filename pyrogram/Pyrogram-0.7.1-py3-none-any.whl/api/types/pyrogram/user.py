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


class User(Object):
    """Attributes:
        ID: ``0xb0700001``

    Args:
        id: ``int`` ``32-bit``
        is_bot: ``bool``
        first_name: ``str``
        last_name (optional): ``str``
        username (optional): ``str``
        language_code (optional): ``str``
        phone_number (optional): ``str``
        photo (optional): :obj:`ChatPhoto <pyrogram.api.types.pyrogram.ChatPhoto>`
    """
    ID = 0xb0700001

    def __init__(self, id, is_bot, first_name, last_name=None, username=None, language_code=None, phone_number=None, photo=None):
        self.id = id  # int
        self.is_bot = is_bot  # Bool
        self.first_name = first_name  # string
        self.last_name = last_name  # flags.0?string
        self.username = username  # flags.1?string
        self.language_code = language_code  # flags.2?string
        self.phone_number = phone_number  # flags.3?string
        self.photo = photo  # flags.4?ChatPhoto

    @staticmethod
    def read(b: BytesIO, *args) -> "User":
        flags = Int.read(b)
        
        id = Int.read(b)
        
        is_bot = Bool.read(b)
        
        first_name = String.read(b)
        
        last_name = String.read(b) if flags & (1 << 0) else None
        username = String.read(b) if flags & (1 << 1) else None
        language_code = String.read(b) if flags & (1 << 2) else None
        phone_number = String.read(b) if flags & (1 << 3) else None
        photo = Object.read(b) if flags & (1 << 4) else None
        
        return User(id, is_bot, first_name, last_name, username, language_code, phone_number, photo)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.last_name is not None else 0
        flags |= (1 << 1) if self.username is not None else 0
        flags |= (1 << 2) if self.language_code is not None else 0
        flags |= (1 << 3) if self.phone_number is not None else 0
        flags |= (1 << 4) if self.photo is not None else 0
        b.write(Int(flags))
        
        b.write(Int(self.id))
        
        b.write(Bool(self.is_bot))
        
        b.write(String(self.first_name))
        
        if self.last_name is not None:
            b.write(String(self.last_name))
        
        if self.username is not None:
            b.write(String(self.username))
        
        if self.language_code is not None:
            b.write(String(self.language_code))
        
        if self.phone_number is not None:
            b.write(String(self.phone_number))
        
        if self.photo is not None:
            b.write(self.photo.write())
        
        return b.getvalue()
