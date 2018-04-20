# coding: utf-8
from __future__ import absolute_import
import logging
from telegram_log import handler

TOKEN = raw_input("Enter TOKEN")
CHAT_ID = int(raw_input("Enter CHAT ID"))

console_logger_name = 'console'
tg_logger_name = 'telegram_bot'

tg_handler = handler.TelegramHandler(token=TOKEN, chat_ids=[CHAT_ID], err_log_name=console_logger_name)
tg_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

tg_logger = logging.getLogger(tg_logger_name)
tg_logger.setLevel(logging.DEBUG)
tg_logger.addHandler(tg_handler)
tg_logger.addHandler(console_handler)

console_logger = logging.getLogger(console_logger_name)
console_logger.setLevel(logging.DEBUG)
console_logger.addHandler(console_handler)



try:
    1 / 0
except:
    tg_logger.exception('error here =(')
