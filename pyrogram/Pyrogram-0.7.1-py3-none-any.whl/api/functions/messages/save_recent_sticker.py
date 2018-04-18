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


class SaveRecentSticker(Object):
    """Attributes:
        ID: ``0x392718f8``

    Args:
        id: Either :obj:`InputDocumentEmpty <pyrogram.api.types.InputDocumentEmpty>` or :obj:`InputDocument <pyrogram.api.types.InputDocument>`
        unsave: ``bool``
        attached (optional): ``bool``

    Raises:
        :obj:`Error <pyrogram.Error>`

    Returns:
        ``bool``
    """
    ID = 0x392718f8

    def __init__(self, id, unsave, attached=None):
        self.attached = attached  # flags.0?true
        self.id = id  # InputDocument
        self.unsave = unsave  # Bool

    @staticmethod
    def read(b: BytesIO, *args) -> "SaveRecentSticker":
        flags = Int.read(b)
        
        attached = True if flags & (1 << 0) else False
        id = Object.read(b)
        
        unsave = Bool.read(b)
        
        return SaveRecentSticker(id, unsave, attached)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.attached is not None else 0
        b.write(Int(flags))
        
        b.write(self.id.write())
        
        b.write(Bool(self.unsave))
        
        return b.getvalue()
