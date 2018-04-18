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


class MessageActionChannelMigrateFrom(Object):
    """Attributes:
        ID: ``0xb055eaee``

    Args:
        title: ``str``
        chat_id: ``int`` ``32-bit``
    """
    ID = 0xb055eaee

    def __init__(self, title, chat_id):
        self.title = title  # string
        self.chat_id = chat_id  # int

    @staticmethod
    def read(b: BytesIO, *args) -> "MessageActionChannelMigrateFrom":
        # No flags
        
        title = String.read(b)
        
        chat_id = Int.read(b)
        
        return MessageActionChannelMigrateFrom(title, chat_id)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.title))
        
        b.write(Int(self.chat_id))
        
        return b.getvalue()
