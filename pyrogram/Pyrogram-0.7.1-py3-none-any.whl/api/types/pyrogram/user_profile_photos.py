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


class UserProfilePhotos(Object):
    """Attributes:
        ID: ``0xb0700014``

    Args:
        total_count: ``int`` ``32-bit``
        photos: List of List of :obj:`PhotoSize <pyrogram.api.types.pyrogram.PhotoSize>`
    """
    ID = 0xb0700014

    def __init__(self, total_count, photos):
        self.total_count = total_count  # int
        self.photos = photos  # Vector<Vector<PhotoSize>>

    @staticmethod
    def read(b: BytesIO, *args) -> "UserProfilePhotos":
        # No flags
        
        total_count = Int.read(b)
        
        photos = Object.read(b)
        
        return UserProfilePhotos(total_count, photos)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.total_count))
        
        b.write(Vector(self.photos))
        
        return b.getvalue()
