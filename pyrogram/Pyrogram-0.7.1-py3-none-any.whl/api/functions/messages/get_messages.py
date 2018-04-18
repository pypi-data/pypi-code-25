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


class GetMessages(Object):
    """Attributes:
        ID: ``0x63c66506``

    Args:
        id: List of either :obj:`InputMessageID <pyrogram.api.types.InputMessageID>`, :obj:`InputMessageReplyTo <pyrogram.api.types.InputMessageReplyTo>` or :obj:`InputMessagePinned <pyrogram.api.types.InputMessagePinned>`

    Raises:
        :obj:`Error <pyrogram.Error>`

    Returns:
        Either :obj:`essages.Messages <pyrogram.api.types.essages.Messages>`, :obj:`essages.MessagesSlice <pyrogram.api.types.essages.MessagesSlice>`, :obj:`essages.ChannelMessages <pyrogram.api.types.essages.ChannelMessages>` or :obj:`essages.MessagesNotModified <pyrogram.api.types.essages.MessagesNotModified>`
    """
    ID = 0x63c66506

    def __init__(self, id):
        self.id = id  # Vector<InputMessage>

    @staticmethod
    def read(b: BytesIO, *args) -> "GetMessages":
        # No flags
        
        id = Object.read(b)
        
        return GetMessages(id)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Vector(self.id))
        
        return b.getvalue()
