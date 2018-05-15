from random import choice
from telegram import Bot, Update
from telegram.ext import MessageHandler, Filters


def voicebitch(bot: Bot, update: Update):
    sticker_set = bot.get_sticker_set('NoVoicePlz')
    bot.send_sticker(update.message.chat_id, choice(sticker_set.stickers).file_id,
                     reply_to_message_id=update.message.message_id)


def setup(dispatcher):
    dispatcher.add_handler(MessageHandler(Filters.voice, voicebitch))
    return dispatcher
