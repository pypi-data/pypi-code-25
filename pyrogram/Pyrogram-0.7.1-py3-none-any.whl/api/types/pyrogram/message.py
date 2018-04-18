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


class Message(Object):
    """Attributes:
        ID: ``0xb0700003``

    Args:
        message_id: ``int`` ``32-bit``
        date: ``int`` ``32-bit``
        chat: :obj:`Chat <pyrogram.api.types.pyrogram.Chat>`
        from_user (optional): :obj:`User <pyrogram.api.types.pyrogram.User>`
        forward_from (optional): :obj:`User <pyrogram.api.types.pyrogram.User>`
        forward_from_chat (optional): :obj:`Chat <pyrogram.api.types.pyrogram.Chat>`
        forward_from_message_id (optional): ``int`` ``32-bit``
        forward_signature (optional): ``str``
        forward_date (optional): ``int`` ``32-bit``
        reply_to_message (optional): :obj:`Message <pyrogram.api.types.pyrogram.Message>`
        edit_date (optional): ``int`` ``32-bit``
        media_group_id (optional): ``str``
        author_signature (optional): ``str``
        text (optional): ``str``
        entities (optional): List of :obj:`MessageEntity <pyrogram.api.types.pyrogram.MessageEntity>`
        caption_entities (optional): List of :obj:`MessageEntity <pyrogram.api.types.pyrogram.MessageEntity>`
        audio (optional): :obj:`Audio <pyrogram.api.types.pyrogram.Audio>`
        document (optional): :obj:`Document <pyrogram.api.types.pyrogram.Document>`
        game (optional): :obj:`Game <pyrogram.api.types.pyrogram.Game>`
        photo (optional): List of :obj:`PhotoSize <pyrogram.api.types.pyrogram.PhotoSize>`
        sticker (optional): :obj:`Sticker <pyrogram.api.types.pyrogram.Sticker>`
        video (optional): :obj:`Video <pyrogram.api.types.pyrogram.Video>`
        voice (optional): :obj:`Voice <pyrogram.api.types.pyrogram.Voice>`
        video_note (optional): :obj:`VideoNote <pyrogram.api.types.pyrogram.VideoNote>`
        caption (optional): ``str``
        contact (optional): :obj:`Contact <pyrogram.api.types.pyrogram.Contact>`
        location (optional): :obj:`Location <pyrogram.api.types.pyrogram.Location>`
        venue (optional): :obj:`Venue <pyrogram.api.types.pyrogram.Venue>`
        new_chat_members (optional): List of :obj:`User <pyrogram.api.types.pyrogram.User>`
        left_chat_member (optional): :obj:`User <pyrogram.api.types.pyrogram.User>`
        new_chat_title (optional): ``str``
        new_chat_photo (optional): List of :obj:`PhotoSize <pyrogram.api.types.pyrogram.PhotoSize>`
        delete_chat_photo (optional): ``bool``
        group_chat_created (optional): ``bool``
        supergroup_chat_created (optional): ``bool``
        channel_chat_created (optional): ``bool``
        migrate_to_chat_id (optional): ``int`` ``32-bit``
        migrate_from_chat_id (optional): ``int`` ``32-bit``
        pinned_message (optional): :obj:`Message <pyrogram.api.types.pyrogram.Message>`
        invoice (optional): :obj:`Invoice <pyrogram.api.types.pyrogram.Invoice>`
        successful_payment (optional): :obj:`SuccessfulPayment <pyrogram.api.types.pyrogram.SuccessfulPayment>`
        connected_website (optional): ``str``
        views (optional): ``int`` ``32-bit``
        via_bot (optional): :obj:`User <pyrogram.api.types.pyrogram.User>`
    """
    ID = 0xb0700003

    def __init__(self, message_id, date, chat, from_user=None, forward_from=None, forward_from_chat=None, forward_from_message_id=None, forward_signature=None, forward_date=None, reply_to_message=None, edit_date=None, media_group_id=None, author_signature=None, text=None, entities=None, caption_entities=None, audio=None, document=None, game=None, photo=None, sticker=None, video=None, voice=None, video_note=None, caption=None, contact=None, location=None, venue=None, new_chat_members=None, left_chat_member=None, new_chat_title=None, new_chat_photo=None, delete_chat_photo=None, group_chat_created=None, supergroup_chat_created=None, channel_chat_created=None, migrate_to_chat_id=None, migrate_from_chat_id=None, pinned_message=None, invoice=None, successful_payment=None, connected_website=None, views=None, via_bot=None):
        self.message_id = message_id  # int
        self.from_user = from_user  # flags.0?User
        self.date = date  # int
        self.chat = chat  # Chat
        self.forward_from = forward_from  # flags.1?User
        self.forward_from_chat = forward_from_chat  # flags.2?Chat
        self.forward_from_message_id = forward_from_message_id  # flags.3?int
        self.forward_signature = forward_signature  # flags.4?string
        self.forward_date = forward_date  # flags.5?int
        self.reply_to_message = reply_to_message  # flags.6?Message
        self.edit_date = edit_date  # flags.7?int
        self.media_group_id = media_group_id  # flags.8?string
        self.author_signature = author_signature  # flags.9?string
        self.text = text  # flags.10?string
        self.entities = entities  # flags.11?Vector<MessageEntity>
        self.caption_entities = caption_entities  # flags.12?Vector<MessageEntity>
        self.audio = audio  # flags.13?Audio
        self.document = document  # flags.14?Document
        self.game = game  # flags.15?Game
        self.photo = photo  # flags.16?Vector<PhotoSize>
        self.sticker = sticker  # flags.17?Sticker
        self.video = video  # flags.18?Video
        self.voice = voice  # flags.19?Voice
        self.video_note = video_note  # flags.20?VideoNote
        self.caption = caption  # flags.21?string
        self.contact = contact  # flags.22?Contact
        self.location = location  # flags.23?Location
        self.venue = venue  # flags.24?Venue
        self.new_chat_members = new_chat_members  # flags.25?Vector<User>
        self.left_chat_member = left_chat_member  # flags.26?User
        self.new_chat_title = new_chat_title  # flags.27?string
        self.new_chat_photo = new_chat_photo  # flags.28?Vector<PhotoSize>
        self.delete_chat_photo = delete_chat_photo  # flags.29?true
        self.group_chat_created = group_chat_created  # flags.30?true
        self.supergroup_chat_created = supergroup_chat_created  # flags.31?true
        self.channel_chat_created = channel_chat_created  # flags.32?true
        self.migrate_to_chat_id = migrate_to_chat_id  # flags.33?int
        self.migrate_from_chat_id = migrate_from_chat_id  # flags.34?int
        self.pinned_message = pinned_message  # flags.35?Message
        self.invoice = invoice  # flags.36?Invoice
        self.successful_payment = successful_payment  # flags.37?SuccessfulPayment
        self.connected_website = connected_website  # flags.38?string
        self.views = views  # flags.39?int
        self.via_bot = via_bot  # flags.40?User

    @staticmethod
    def read(b: BytesIO, *args) -> "Message":
        flags = Int.read(b)
        
        message_id = Int.read(b)
        
        from_user = Object.read(b) if flags & (1 << 0) else None
        
        date = Int.read(b)
        
        chat = Object.read(b)
        
        forward_from = Object.read(b) if flags & (1 << 1) else None
        
        forward_from_chat = Object.read(b) if flags & (1 << 2) else None
        
        forward_from_message_id = Int.read(b) if flags & (1 << 3) else None
        forward_signature = String.read(b) if flags & (1 << 4) else None
        forward_date = Int.read(b) if flags & (1 << 5) else None
        reply_to_message = Object.read(b) if flags & (1 << 6) else None
        
        edit_date = Int.read(b) if flags & (1 << 7) else None
        media_group_id = String.read(b) if flags & (1 << 8) else None
        author_signature = String.read(b) if flags & (1 << 9) else None
        text = String.read(b) if flags & (1 << 10) else None
        entities = Object.read(b) if flags & (1 << 11) else []
        
        caption_entities = Object.read(b) if flags & (1 << 12) else []
        
        audio = Object.read(b) if flags & (1 << 13) else None
        
        document = Object.read(b) if flags & (1 << 14) else None
        
        game = Object.read(b) if flags & (1 << 15) else None
        
        photo = Object.read(b) if flags & (1 << 16) else []
        
        sticker = Object.read(b) if flags & (1 << 17) else None
        
        video = Object.read(b) if flags & (1 << 18) else None
        
        voice = Object.read(b) if flags & (1 << 19) else None
        
        video_note = Object.read(b) if flags & (1 << 20) else None
        
        caption = String.read(b) if flags & (1 << 21) else None
        contact = Object.read(b) if flags & (1 << 22) else None
        
        location = Object.read(b) if flags & (1 << 23) else None
        
        venue = Object.read(b) if flags & (1 << 24) else None
        
        new_chat_members = Object.read(b) if flags & (1 << 25) else []
        
        left_chat_member = Object.read(b) if flags & (1 << 26) else None
        
        new_chat_title = String.read(b) if flags & (1 << 27) else None
        new_chat_photo = Object.read(b) if flags & (1 << 28) else []
        
        delete_chat_photo = True if flags & (1 << 29) else False
        group_chat_created = True if flags & (1 << 30) else False
        supergroup_chat_created = True if flags & (1 << 31) else False
        channel_chat_created = True if flags & (1 << 32) else False
        migrate_to_chat_id = Int.read(b) if flags & (1 << 33) else None
        migrate_from_chat_id = Int.read(b) if flags & (1 << 34) else None
        pinned_message = Object.read(b) if flags & (1 << 35) else None
        
        invoice = Object.read(b) if flags & (1 << 36) else None
        
        successful_payment = Object.read(b) if flags & (1 << 37) else None
        
        connected_website = String.read(b) if flags & (1 << 38) else None
        views = Int.read(b) if flags & (1 << 39) else None
        via_bot = Object.read(b) if flags & (1 << 40) else None
        
        return Message(message_id, date, chat, from_user, forward_from, forward_from_chat, forward_from_message_id, forward_signature, forward_date, reply_to_message, edit_date, media_group_id, author_signature, text, entities, caption_entities, audio, document, game, photo, sticker, video, voice, video_note, caption, contact, location, venue, new_chat_members, left_chat_member, new_chat_title, new_chat_photo, delete_chat_photo, group_chat_created, supergroup_chat_created, channel_chat_created, migrate_to_chat_id, migrate_from_chat_id, pinned_message, invoice, successful_payment, connected_website, views, via_bot)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.from_user is not None else 0
        flags |= (1 << 1) if self.forward_from is not None else 0
        flags |= (1 << 2) if self.forward_from_chat is not None else 0
        flags |= (1 << 3) if self.forward_from_message_id is not None else 0
        flags |= (1 << 4) if self.forward_signature is not None else 0
        flags |= (1 << 5) if self.forward_date is not None else 0
        flags |= (1 << 6) if self.reply_to_message is not None else 0
        flags |= (1 << 7) if self.edit_date is not None else 0
        flags |= (1 << 8) if self.media_group_id is not None else 0
        flags |= (1 << 9) if self.author_signature is not None else 0
        flags |= (1 << 10) if self.text is not None else 0
        flags |= (1 << 11) if self.entities is not None else 0
        flags |= (1 << 12) if self.caption_entities is not None else 0
        flags |= (1 << 13) if self.audio is not None else 0
        flags |= (1 << 14) if self.document is not None else 0
        flags |= (1 << 15) if self.game is not None else 0
        flags |= (1 << 16) if self.photo is not None else 0
        flags |= (1 << 17) if self.sticker is not None else 0
        flags |= (1 << 18) if self.video is not None else 0
        flags |= (1 << 19) if self.voice is not None else 0
        flags |= (1 << 20) if self.video_note is not None else 0
        flags |= (1 << 21) if self.caption is not None else 0
        flags |= (1 << 22) if self.contact is not None else 0
        flags |= (1 << 23) if self.location is not None else 0
        flags |= (1 << 24) if self.venue is not None else 0
        flags |= (1 << 25) if self.new_chat_members is not None else 0
        flags |= (1 << 26) if self.left_chat_member is not None else 0
        flags |= (1 << 27) if self.new_chat_title is not None else 0
        flags |= (1 << 28) if self.new_chat_photo is not None else 0
        flags |= (1 << 29) if self.delete_chat_photo is not None else 0
        flags |= (1 << 30) if self.group_chat_created is not None else 0
        flags |= (1 << 31) if self.supergroup_chat_created is not None else 0
        flags |= (1 << 32) if self.channel_chat_created is not None else 0
        flags |= (1 << 33) if self.migrate_to_chat_id is not None else 0
        flags |= (1 << 34) if self.migrate_from_chat_id is not None else 0
        flags |= (1 << 35) if self.pinned_message is not None else 0
        flags |= (1 << 36) if self.invoice is not None else 0
        flags |= (1 << 37) if self.successful_payment is not None else 0
        flags |= (1 << 38) if self.connected_website is not None else 0
        flags |= (1 << 39) if self.views is not None else 0
        flags |= (1 << 40) if self.via_bot is not None else 0
        b.write(Int(flags))
        
        b.write(Int(self.message_id))
        
        if self.from_user is not None:
            b.write(self.from_user.write())
        
        b.write(Int(self.date))
        
        b.write(self.chat.write())
        
        if self.forward_from is not None:
            b.write(self.forward_from.write())
        
        if self.forward_from_chat is not None:
            b.write(self.forward_from_chat.write())
        
        if self.forward_from_message_id is not None:
            b.write(Int(self.forward_from_message_id))
        
        if self.forward_signature is not None:
            b.write(String(self.forward_signature))
        
        if self.forward_date is not None:
            b.write(Int(self.forward_date))
        
        if self.reply_to_message is not None:
            b.write(self.reply_to_message.write())
        
        if self.edit_date is not None:
            b.write(Int(self.edit_date))
        
        if self.media_group_id is not None:
            b.write(String(self.media_group_id))
        
        if self.author_signature is not None:
            b.write(String(self.author_signature))
        
        if self.text is not None:
            b.write(String(self.text))
        
        if self.entities is not None:
            b.write(Vector(self.entities))
        
        if self.caption_entities is not None:
            b.write(Vector(self.caption_entities))
        
        if self.audio is not None:
            b.write(self.audio.write())
        
        if self.document is not None:
            b.write(self.document.write())
        
        if self.game is not None:
            b.write(self.game.write())
        
        if self.photo is not None:
            b.write(Vector(self.photo))
        
        if self.sticker is not None:
            b.write(self.sticker.write())
        
        if self.video is not None:
            b.write(self.video.write())
        
        if self.voice is not None:
            b.write(self.voice.write())
        
        if self.video_note is not None:
            b.write(self.video_note.write())
        
        if self.caption is not None:
            b.write(String(self.caption))
        
        if self.contact is not None:
            b.write(self.contact.write())
        
        if self.location is not None:
            b.write(self.location.write())
        
        if self.venue is not None:
            b.write(self.venue.write())
        
        if self.new_chat_members is not None:
            b.write(Vector(self.new_chat_members))
        
        if self.left_chat_member is not None:
            b.write(self.left_chat_member.write())
        
        if self.new_chat_title is not None:
            b.write(String(self.new_chat_title))
        
        if self.new_chat_photo is not None:
            b.write(Vector(self.new_chat_photo))
        
        if self.migrate_to_chat_id is not None:
            b.write(Int(self.migrate_to_chat_id))
        
        if self.migrate_from_chat_id is not None:
            b.write(Int(self.migrate_from_chat_id))
        
        if self.pinned_message is not None:
            b.write(self.pinned_message.write())
        
        if self.invoice is not None:
            b.write(self.invoice.write())
        
        if self.successful_payment is not None:
            b.write(self.successful_payment.write())
        
        if self.connected_website is not None:
            b.write(String(self.connected_website))
        
        if self.views is not None:
            b.write(Int(self.views))
        
        if self.via_bot is not None:
            b.write(self.via_bot.write())
        
        return b.getvalue()
