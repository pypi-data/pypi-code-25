from telegram import Bot, Update, Chat
from telegram.ext import MessageHandler, Filters, CommandHandler
from dynamic_preferences.registries import global_preferences_registry


global_preferences = global_preferences_registry.manager()


def report(bot: Bot, update: Update):
    if update.message.chat.type in [Chat.GROUP, Chat.SUPERGROUP] and update.message.chat.username:
        bot.send_message(global_preferences['lprutils__notifications_chat_id'],
                         f'https://t.me/{update.message.chat.username}/{update.message.message_id}')
    else:
        update.message.forward(global_preferences['lprutils__notifications_chat_id'])


def remove_cmd(bot: Bot, update: Update):
    update.message.delete()


def setup(dispatcher):
    dispatcher.add_handler(CommandHandler('report', report))
    dispatcher.add_handler(MessageHandler(Filters.group &
                                          (Filters.contact | Filters.text & Filters.regex(r'^[!/].*')), remove_cmd))
    return dispatcher
