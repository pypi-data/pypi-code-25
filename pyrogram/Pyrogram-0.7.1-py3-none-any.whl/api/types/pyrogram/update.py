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


class Update(Object):
    """Attributes:
        ID: ``0xb0700000``

    Args:
        update_id: ``int`` ``32-bit``
        message (optional): :obj:`Message <pyrogram.api.types.pyrogram.Message>`
        edited_message (optional): :obj:`Message <pyrogram.api.types.pyrogram.Message>`
        channel_post (optional): :obj:`Message <pyrogram.api.types.pyrogram.Message>`
        edited_channel_post (optional): :obj:`Message <pyrogram.api.types.pyrogram.Message>`
        inline_query (optional): :obj:`InlineQuery <pyrogram.api.types.pyrogram.InlineQuery>`
        chosen_inline_result (optional): :obj:`ChosenInlineResult <pyrogram.api.types.pyrogram.ChosenInlineResult>`
        callback_query (optional): :obj:`CallbackQuery <pyrogram.api.types.pyrogram.CallbackQuery>`
        shipping_query (optional): :obj:`ShippingQuery <pyrogram.api.types.pyrogram.ShippingQuery>`
        pre_checkout_query (optional): :obj:`PreCheckoutQuery <pyrogram.api.types.pyrogram.PreCheckoutQuery>`
    """
    ID = 0xb0700000

    def __init__(self, update_id, message=None, edited_message=None, channel_post=None, edited_channel_post=None, inline_query=None, chosen_inline_result=None, callback_query=None, shipping_query=None, pre_checkout_query=None):
        self.update_id = update_id  # int
        self.message = message  # flags.0?Message
        self.edited_message = edited_message  # flags.1?Message
        self.channel_post = channel_post  # flags.2?Message
        self.edited_channel_post = edited_channel_post  # flags.3?Message
        self.inline_query = inline_query  # flags.4?InlineQuery
        self.chosen_inline_result = chosen_inline_result  # flags.5?ChosenInlineResult
        self.callback_query = callback_query  # flags.6?CallbackQuery
        self.shipping_query = shipping_query  # flags.7?ShippingQuery
        self.pre_checkout_query = pre_checkout_query  # flags.8?PreCheckoutQuery

    @staticmethod
    def read(b: BytesIO, *args) -> "Update":
        flags = Int.read(b)
        
        update_id = Int.read(b)
        
        message = Object.read(b) if flags & (1 << 0) else None
        
        edited_message = Object.read(b) if flags & (1 << 1) else None
        
        channel_post = Object.read(b) if flags & (1 << 2) else None
        
        edited_channel_post = Object.read(b) if flags & (1 << 3) else None
        
        inline_query = Object.read(b) if flags & (1 << 4) else None
        
        chosen_inline_result = Object.read(b) if flags & (1 << 5) else None
        
        callback_query = Object.read(b) if flags & (1 << 6) else None
        
        shipping_query = Object.read(b) if flags & (1 << 7) else None
        
        pre_checkout_query = Object.read(b) if flags & (1 << 8) else None
        
        return Update(update_id, message, edited_message, channel_post, edited_channel_post, inline_query, chosen_inline_result, callback_query, shipping_query, pre_checkout_query)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.message is not None else 0
        flags |= (1 << 1) if self.edited_message is not None else 0
        flags |= (1 << 2) if self.channel_post is not None else 0
        flags |= (1 << 3) if self.edited_channel_post is not None else 0
        flags |= (1 << 4) if self.inline_query is not None else 0
        flags |= (1 << 5) if self.chosen_inline_result is not None else 0
        flags |= (1 << 6) if self.callback_query is not None else 0
        flags |= (1 << 7) if self.shipping_query is not None else 0
        flags |= (1 << 8) if self.pre_checkout_query is not None else 0
        b.write(Int(flags))
        
        b.write(Int(self.update_id))
        
        if self.message is not None:
            b.write(self.message.write())
        
        if self.edited_message is not None:
            b.write(self.edited_message.write())
        
        if self.channel_post is not None:
            b.write(self.channel_post.write())
        
        if self.edited_channel_post is not None:
            b.write(self.edited_channel_post.write())
        
        if self.inline_query is not None:
            b.write(self.inline_query.write())
        
        if self.chosen_inline_result is not None:
            b.write(self.chosen_inline_result.write())
        
        if self.callback_query is not None:
            b.write(self.callback_query.write())
        
        if self.shipping_query is not None:
            b.write(self.shipping_query.write())
        
        if self.pre_checkout_query is not None:
            b.write(self.pre_checkout_query.write())
        
        return b.getvalue()
