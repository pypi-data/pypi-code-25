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


class Chat(Object):
    """Attributes:
        ID: ``0xb0700002``

    Args:
        id: ``int`` ``32-bit``
        type: ``str``
        title (optional): ``str``
        username (optional): ``str``
        first_name (optional): ``str``
        last_name (optional): ``str``
        all_members_are_administrators (optional): ``bool``
        photo (optional): :obj:`ChatPhoto <pyrogram.api.types.pyrogram.ChatPhoto>`
        description (optional): ``str``
        invite_link (optional): ``str``
        pinned_message (optional): :obj:`Message <pyrogram.api.types.pyrogram.Message>`
        sticker_set_name (optional): ``str``
        can_set_sticker_set (optional): ``bool``
    """
    ID = 0xb0700002

    def __init__(self, id, type, title=None, username=None, first_name=None, last_name=None, all_members_are_administrators=None, photo=None, description=None, invite_link=None, pinned_message=None, sticker_set_name=None, can_set_sticker_set=None):
        self.id = id  # int
        self.type = type  # string
        self.title = title  # flags.0?string
        self.username = username  # flags.1?string
        self.first_name = first_name  # flags.2?string
        self.last_name = last_name  # flags.3?string
        self.all_members_are_administrators = all_members_are_administrators  # flags.4?Bool
        self.photo = photo  # flags.5?ChatPhoto
        self.description = description  # flags.6?string
        self.invite_link = invite_link  # flags.7?string
        self.pinned_message = pinned_message  # flags.8?Message
        self.sticker_set_name = sticker_set_name  # flags.9?string
        self.can_set_sticker_set = can_set_sticker_set  # flags.10?Bool

    @staticmethod
    def read(b: BytesIO, *args) -> "Chat":
        flags = Int.read(b)
        
        id = Int.read(b)
        
        type = String.read(b)
        
        title = String.read(b) if flags & (1 << 0) else None
        username = String.read(b) if flags & (1 << 1) else None
        first_name = String.read(b) if flags & (1 << 2) else None
        last_name = String.read(b) if flags & (1 << 3) else None
        all_members_are_administrators = Bool.read(b) if flags & (1 << 4) else None
        photo = Object.read(b) if flags & (1 << 5) else None
        
        description = String.read(b) if flags & (1 << 6) else None
        invite_link = String.read(b) if flags & (1 << 7) else None
        pinned_message = Object.read(b) if flags & (1 << 8) else None
        
        sticker_set_name = String.read(b) if flags & (1 << 9) else None
        can_set_sticker_set = Bool.read(b) if flags & (1 << 10) else None
        return Chat(id, type, title, username, first_name, last_name, all_members_are_administrators, photo, description, invite_link, pinned_message, sticker_set_name, can_set_sticker_set)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.title is not None else 0
        flags |= (1 << 1) if self.username is not None else 0
        flags |= (1 << 2) if self.first_name is not None else 0
        flags |= (1 << 3) if self.last_name is not None else 0
        flags |= (1 << 4) if self.all_members_are_administrators is not None else 0
        flags |= (1 << 5) if self.photo is not None else 0
        flags |= (1 << 6) if self.description is not None else 0
        flags |= (1 << 7) if self.invite_link is not None else 0
        flags |= (1 << 8) if self.pinned_message is not None else 0
        flags |= (1 << 9) if self.sticker_set_name is not None else 0
        flags |= (1 << 10) if self.can_set_sticker_set is not None else 0
        b.write(Int(flags))
        
        b.write(Int(self.id))
        
        b.write(String(self.type))
        
        if self.title is not None:
            b.write(String(self.title))
        
        if self.username is not None:
            b.write(String(self.username))
        
        if self.first_name is not None:
            b.write(String(self.first_name))
        
        if self.last_name is not None:
            b.write(String(self.last_name))
        
        if self.all_members_are_administrators is not None:
            b.write(Bool(self.all_members_are_administrators))
        
        if self.photo is not None:
            b.write(self.photo.write())
        
        if self.description is not None:
            b.write(String(self.description))
        
        if self.invite_link is not None:
            b.write(String(self.invite_link))
        
        if self.pinned_message is not None:
            b.write(self.pinned_message.write())
        
        if self.sticker_set_name is not None:
            b.write(String(self.sticker_set_name))
        
        if self.can_set_sticker_set is not None:
            b.write(Bool(self.can_set_sticker_set))
        
        return b.getvalue()
