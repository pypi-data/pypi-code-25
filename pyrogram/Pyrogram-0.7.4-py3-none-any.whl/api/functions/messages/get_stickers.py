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


class GetStickers(Object):
    """Attributes:
        ID: ``0x85cb5182``

    Args:
        emoticon: ``str``
        hash: ``str``
        exclude_featured (optional): ``bool``

    Raises:
        :obj:`Error <pyrogram.Error>`

    Returns:
        Either :obj:`messages.StickersNotModified <pyrogram.api.types.messages.StickersNotModified>` or :obj:`messages.Stickers <pyrogram.api.types.messages.Stickers>`
    """

    ID = 0x85cb5182

    def __init__(self, emoticon: str, hash: str, exclude_featured: bool = None):
        self.exclude_featured = exclude_featured  # flags.0?true
        self.emoticon = emoticon  # string
        self.hash = hash  # string

    @staticmethod
    def read(b: BytesIO, *args) -> "GetStickers":
        flags = Int.read(b)
        
        exclude_featured = True if flags & (1 << 0) else False
        emoticon = String.read(b)
        
        hash = String.read(b)
        
        return GetStickers(emoticon, hash, exclude_featured)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.exclude_featured is not None else 0
        b.write(Int(flags))
        
        b.write(String(self.emoticon))
        
        b.write(String(self.hash))
        
        return b.getvalue()
