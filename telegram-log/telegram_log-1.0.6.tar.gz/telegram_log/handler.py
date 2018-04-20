# coding: utf-8
import telegram
import cgitb
import io
import datetime
import logging
from telegram.utils.request import Request

message_limit = 4096
caption_limit = 200
context_width = 11
exc_msg = 'Telegram exception'
file_pattern = 'python_tb_%Y-%m-%d_%H_%M_%S.html'
encoding = 'utf-8'


class TelegramHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        token, chat_ids, err_log_name = kwargs.pop('token'), kwargs.pop('chat_ids'), kwargs.pop('err_log_name')
        proxy_url = kwargs.pop('proxy_url', None)
        request = Request(proxy_url=proxy_url) if proxy_url else None
        self.bot = telegram.Bot(token, request=request)
        self.chat_ids = chat_ids
        self.logger = logging.getLogger(err_log_name)
        logging.Handler.__init__(self, *args, **kwargs)

    @staticmethod
    def get_tb_file(exc_info):
        buffer = io.BytesIO()
        cgitb.Hook(context=11, file=buffer).handle(info=exc_info)
        buffer.seek(0)
        return buffer

    @staticmethod
    def prepare(unicode_or_str, length):
        message = unicode_or_str
        if isinstance(message, str):
            # Перед срезом, нужно привести к юникоду, т.к. срез в str делается побайтово
            message = message.decode(encoding)
        message = message[:length]
        message = message.encode(encoding)
        return message

    def emit(self, record):
        try:
            if record.exc_info:
                tb_file = self.get_tb_file(record.exc_info)
            else:
                tb_file = None
            for chat_id in self.chat_ids:
                if tb_file:
                    tb_file.seek(0)
                    exc_info = record.exc_info
                    record.exc_info = None
                    caption = self.prepare(self.format(record), caption_limit)
                    record.exc_info = exc_info
                    self.bot.send_document(chat_id,
                                           tb_file,
                                           datetime.datetime.now().strftime(file_pattern),
                                           caption=caption)
                else:
                    message = self.prepare(self.format(record), message_limit)
                    self.bot.sendMessage(chat_id, message)
            if tb_file:
                tb_file.close()
        except BaseException:
            if self.logger:
                self.logger.exception(exc_msg)

    def send_document(self, fobj, filename, caption=None):
        try:
            for chat_id in self.chat_ids:
                self.bot.send_document(chat_id, fobj, filename, caption=caption)
        except BaseException:
            if self.logger:
                self.logger.exception(exc_msg)
