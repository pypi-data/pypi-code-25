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


class GetFavedStickers(Object):
    """Attributes:
        ID: ``0x21ce0b0e``

    Args:
        hash: ``int`` ``32-bit``

    Raises:
        :obj:`Error <pyrogram.Error>`

    Returns:
        Either :obj:`essages.FavedStickersNotModified <pyrogram.api.types.essages.FavedStickersNotModified>` or :obj:`essages.FavedStickers <pyrogram.api.types.essages.FavedStickers>`
    """
    ID = 0x21ce0b0e

    def __init__(self, hash):
        self.hash = hash  # int

    @staticmethod
    def read(b: BytesIO, *args) -> "GetFavedStickers":
        # No flags
        
        hash = Int.read(b)
        
        return GetFavedStickers(hash)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.hash))
        
        return b.getvalue()
