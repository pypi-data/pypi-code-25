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


class ChatMember(Object):
    """Attributes:
        ID: ``0xb0700016``

    Args:
        user: :obj:`User <pyrogram.api.types.pyrogram.User>`
        status: ``str``
        until_date (optional): ``int`` ``32-bit``
        can_be_edited (optional): ``bool``
        can_change_info (optional): ``bool``
        can_post_messages (optional): ``bool``
        can_edit_messages (optional): ``bool``
        can_delete_messages (optional): ``bool``
        can_invite_users (optional): ``bool``
        can_restrict_members (optional): ``bool``
        can_pin_messages (optional): ``bool``
        can_promote_members (optional): ``bool``
        can_send_messages (optional): ``bool``
        can_send_media_messages (optional): ``bool``
        can_send_other_messages (optional): ``bool``
        can_add_web_page_previews (optional): ``bool``
    """
    ID = 0xb0700016

    def __init__(self, user, status, until_date=None, can_be_edited=None, can_change_info=None, can_post_messages=None, can_edit_messages=None, can_delete_messages=None, can_invite_users=None, can_restrict_members=None, can_pin_messages=None, can_promote_members=None, can_send_messages=None, can_send_media_messages=None, can_send_other_messages=None, can_add_web_page_previews=None):
        self.user = user  # User
        self.status = status  # string
        self.until_date = until_date  # flags.0?int
        self.can_be_edited = can_be_edited  # flags.1?Bool
        self.can_change_info = can_change_info  # flags.2?Bool
        self.can_post_messages = can_post_messages  # flags.3?Bool
        self.can_edit_messages = can_edit_messages  # flags.4?Bool
        self.can_delete_messages = can_delete_messages  # flags.5?Bool
        self.can_invite_users = can_invite_users  # flags.6?Bool
        self.can_restrict_members = can_restrict_members  # flags.7?Bool
        self.can_pin_messages = can_pin_messages  # flags.8?Bool
        self.can_promote_members = can_promote_members  # flags.9?Bool
        self.can_send_messages = can_send_messages  # flags.10?Bool
        self.can_send_media_messages = can_send_media_messages  # flags.11?Bool
        self.can_send_other_messages = can_send_other_messages  # flags.12?Bool
        self.can_add_web_page_previews = can_add_web_page_previews  # flags.13?Bool

    @staticmethod
    def read(b: BytesIO, *args) -> "ChatMember":
        flags = Int.read(b)
        
        user = Object.read(b)
        
        status = String.read(b)
        
        until_date = Int.read(b) if flags & (1 << 0) else None
        can_be_edited = Bool.read(b) if flags & (1 << 1) else None
        can_change_info = Bool.read(b) if flags & (1 << 2) else None
        can_post_messages = Bool.read(b) if flags & (1 << 3) else None
        can_edit_messages = Bool.read(b) if flags & (1 << 4) else None
        can_delete_messages = Bool.read(b) if flags & (1 << 5) else None
        can_invite_users = Bool.read(b) if flags & (1 << 6) else None
        can_restrict_members = Bool.read(b) if flags & (1 << 7) else None
        can_pin_messages = Bool.read(b) if flags & (1 << 8) else None
        can_promote_members = Bool.read(b) if flags & (1 << 9) else None
        can_send_messages = Bool.read(b) if flags & (1 << 10) else None
        can_send_media_messages = Bool.read(b) if flags & (1 << 11) else None
        can_send_other_messages = Bool.read(b) if flags & (1 << 12) else None
        can_add_web_page_previews = Bool.read(b) if flags & (1 << 13) else None
        return ChatMember(user, status, until_date, can_be_edited, can_change_info, can_post_messages, can_edit_messages, can_delete_messages, can_invite_users, can_restrict_members, can_pin_messages, can_promote_members, can_send_messages, can_send_media_messages, can_send_other_messages, can_add_web_page_previews)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.until_date is not None else 0
        flags |= (1 << 1) if self.can_be_edited is not None else 0
        flags |= (1 << 2) if self.can_change_info is not None else 0
        flags |= (1 << 3) if self.can_post_messages is not None else 0
        flags |= (1 << 4) if self.can_edit_messages is not None else 0
        flags |= (1 << 5) if self.can_delete_messages is not None else 0
        flags |= (1 << 6) if self.can_invite_users is not None else 0
        flags |= (1 << 7) if self.can_restrict_members is not None else 0
        flags |= (1 << 8) if self.can_pin_messages is not None else 0
        flags |= (1 << 9) if self.can_promote_members is not None else 0
        flags |= (1 << 10) if self.can_send_messages is not None else 0
        flags |= (1 << 11) if self.can_send_media_messages is not None else 0
        flags |= (1 << 12) if self.can_send_other_messages is not None else 0
        flags |= (1 << 13) if self.can_add_web_page_previews is not None else 0
        b.write(Int(flags))
        
        b.write(self.user.write())
        
        b.write(String(self.status))
        
        if self.until_date is not None:
            b.write(Int(self.until_date))
        
        if self.can_be_edited is not None:
            b.write(Bool(self.can_be_edited))
        
        if self.can_change_info is not None:
            b.write(Bool(self.can_change_info))
        
        if self.can_post_messages is not None:
            b.write(Bool(self.can_post_messages))
        
        if self.can_edit_messages is not None:
            b.write(Bool(self.can_edit_messages))
        
        if self.can_delete_messages is not None:
            b.write(Bool(self.can_delete_messages))
        
        if self.can_invite_users is not None:
            b.write(Bool(self.can_invite_users))
        
        if self.can_restrict_members is not None:
            b.write(Bool(self.can_restrict_members))
        
        if self.can_pin_messages is not None:
            b.write(Bool(self.can_pin_messages))
        
        if self.can_promote_members is not None:
            b.write(Bool(self.can_promote_members))
        
        if self.can_send_messages is not None:
            b.write(Bool(self.can_send_messages))
        
        if self.can_send_media_messages is not None:
            b.write(Bool(self.can_send_media_messages))
        
        if self.can_send_other_messages is not None:
            b.write(Bool(self.can_send_other_messages))
        
        if self.can_add_web_page_previews is not None:
            b.write(Bool(self.can_add_web_page_previews))
        
        return b.getvalue()
