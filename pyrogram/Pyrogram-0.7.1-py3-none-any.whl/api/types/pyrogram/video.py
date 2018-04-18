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


class Video(Object):
    """Attributes:
        ID: ``0xb0700008``

    Args:
        file_id: ``str``
        width: ``int`` ``32-bit``
        height: ``int`` ``32-bit``
        duration: ``int`` ``32-bit``
        thumb (optional): :obj:`PhotoSize <pyrogram.api.types.pyrogram.PhotoSize>`
        file_name (optional): ``str``
        mime_type (optional): ``str``
        file_size (optional): ``int`` ``32-bit``
        date (optional): ``int`` ``32-bit``
    """
    ID = 0xb0700008

    def __init__(self, file_id, width, height, duration, thumb=None, file_name=None, mime_type=None, file_size=None, date=None):
        self.file_id = file_id  # string
        self.thumb = thumb  # flags.0?PhotoSize
        self.file_name = file_name  # flags.1?string
        self.mime_type = mime_type  # flags.2?string
        self.file_size = file_size  # flags.3?int
        self.date = date  # flags.4?int
        self.width = width  # int
        self.height = height  # int
        self.duration = duration  # int

    @staticmethod
    def read(b: BytesIO, *args) -> "Video":
        flags = Int.read(b)
        
        file_id = String.read(b)
        
        thumb = Object.read(b) if flags & (1 << 0) else None
        
        file_name = String.read(b) if flags & (1 << 1) else None
        mime_type = String.read(b) if flags & (1 << 2) else None
        file_size = Int.read(b) if flags & (1 << 3) else None
        date = Int.read(b) if flags & (1 << 4) else None
        width = Int.read(b)
        
        height = Int.read(b)
        
        duration = Int.read(b)
        
        return Video(file_id, width, height, duration, thumb, file_name, mime_type, file_size, date)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.thumb is not None else 0
        flags |= (1 << 1) if self.file_name is not None else 0
        flags |= (1 << 2) if self.mime_type is not None else 0
        flags |= (1 << 3) if self.file_size is not None else 0
        flags |= (1 << 4) if self.date is not None else 0
        b.write(Int(flags))
        
        b.write(String(self.file_id))
        
        if self.thumb is not None:
            b.write(self.thumb.write())
        
        if self.file_name is not None:
            b.write(String(self.file_name))
        
        if self.mime_type is not None:
            b.write(String(self.mime_type))
        
        if self.file_size is not None:
            b.write(Int(self.file_size))
        
        if self.date is not None:
            b.write(Int(self.date))
        
        b.write(Int(self.width))
        
        b.write(Int(self.height))
        
        b.write(Int(self.duration))
        
        return b.getvalue()
