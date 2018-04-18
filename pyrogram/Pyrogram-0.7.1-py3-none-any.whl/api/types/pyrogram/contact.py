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


class Contact(Object):
    """Attributes:
        ID: ``0xb0700011``

    Args:
        phone_number: ``str``
        first_name: ``str``
        last_name (optional): ``str``
        user_id (optional): ``int`` ``32-bit``
    """
    ID = 0xb0700011

    def __init__(self, phone_number, first_name, last_name=None, user_id=None):
        self.phone_number = phone_number  # string
        self.first_name = first_name  # string
        self.last_name = last_name  # flags.0?string
        self.user_id = user_id  # flags.1?int

    @staticmethod
    def read(b: BytesIO, *args) -> "Contact":
        flags = Int.read(b)
        
        phone_number = String.read(b)
        
        first_name = String.read(b)
        
        last_name = String.read(b) if flags & (1 << 0) else None
        user_id = Int.read(b) if flags & (1 << 1) else None
        return Contact(phone_number, first_name, last_name, user_id)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.last_name is not None else 0
        flags |= (1 << 1) if self.user_id is not None else 0
        b.write(Int(flags))
        
        b.write(String(self.phone_number))
        
        b.write(String(self.first_name))
        
        if self.last_name is not None:
            b.write(String(self.last_name))
        
        if self.user_id is not None:
            b.write(Int(self.user_id))
        
        return b.getvalue()
