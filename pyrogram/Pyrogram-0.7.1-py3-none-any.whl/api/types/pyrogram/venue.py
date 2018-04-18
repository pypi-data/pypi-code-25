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


class Venue(Object):
    """Attributes:
        ID: ``0xb0700013``

    Args:
        location: :obj:`Location <pyrogram.api.types.pyrogram.Location>`
        title: ``str``
        address: ``str``
        foursquare_id (optional): ``str``
    """
    ID = 0xb0700013

    def __init__(self, location, title, address, foursquare_id=None):
        self.location = location  # Location
        self.title = title  # string
        self.address = address  # string
        self.foursquare_id = foursquare_id  # flags.0?string

    @staticmethod
    def read(b: BytesIO, *args) -> "Venue":
        flags = Int.read(b)
        
        location = Object.read(b)
        
        title = String.read(b)
        
        address = String.read(b)
        
        foursquare_id = String.read(b) if flags & (1 << 0) else None
        return Venue(location, title, address, foursquare_id)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.foursquare_id is not None else 0
        b.write(Int(flags))
        
        b.write(self.location.write())
        
        b.write(String(self.title))
        
        b.write(String(self.address))
        
        if self.foursquare_id is not None:
            b.write(String(self.foursquare_id))
        
        return b.getvalue()
