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


class PhotoSize(Object):
    """Attributes:
        ID: ``0xb0700005``

    Args:
        file_id: ``str``
        width: ``int`` ``32-bit``
        height: ``int`` ``32-bit``
        file_size (optional): ``int`` ``32-bit``
        date (optional): ``int`` ``32-bit``
    """
    ID = 0xb0700005

    def __init__(self, file_id, width, height, file_size=None, date=None):
        self.file_id = file_id  # string
        self.file_size = file_size  # flags.0?int
        self.date = date  # flags.1?int
        self.width = width  # int
        self.height = height  # int

    @staticmethod
    def read(b: BytesIO, *args) -> "PhotoSize":
        flags = Int.read(b)
        
        file_id = String.read(b)
        
        file_size = Int.read(b) if flags & (1 << 0) else None
        date = Int.read(b) if flags & (1 << 1) else None
        width = Int.read(b)
        
        height = Int.read(b)
        
        return PhotoSize(file_id, width, height, file_size, date)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.file_size is not None else 0
        flags |= (1 << 1) if self.date is not None else 0
        b.write(Int(flags))
        
        b.write(String(self.file_id))
        
        if self.file_size is not None:
            b.write(Int(self.file_size))
        
        if self.date is not None:
            b.write(Int(self.date))
        
        b.write(Int(self.width))
        
        b.write(Int(self.height))
        
        return b.getvalue()
