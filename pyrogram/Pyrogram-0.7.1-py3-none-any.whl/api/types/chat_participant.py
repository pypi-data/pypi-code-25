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


class ChatParticipant(Object):
    """Attributes:
        ID: ``0xc8d7493e``

    Args:
        user_id: ``int`` ``32-bit``
        inviter_id: ``int`` ``32-bit``
        date: ``int`` ``32-bit``
    """
    ID = 0xc8d7493e

    def __init__(self, user_id, inviter_id, date):
        self.user_id = user_id  # int
        self.inviter_id = inviter_id  # int
        self.date = date  # int

    @staticmethod
    def read(b: BytesIO, *args) -> "ChatParticipant":
        # No flags
        
        user_id = Int.read(b)
        
        inviter_id = Int.read(b)
        
        date = Int.read(b)
        
        return ChatParticipant(user_id, inviter_id, date)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.user_id))
        
        b.write(Int(self.inviter_id))
        
        b.write(Int(self.date))
        
        return b.getvalue()
