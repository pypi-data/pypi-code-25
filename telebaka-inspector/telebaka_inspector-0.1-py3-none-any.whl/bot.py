import json
from datetime import date
import io
import os
import tempfile
import uuid

from PIL import Image
from django.conf import settings
from django.urls import reverse

from telegram import Bot, Update
from telegram.error import BadRequest
from telegram.ext import MessageHandler, Filters, CommandHandler

from telebaka_inspector.models import Message


def inspector(bot: Bot, update: Update):
    msg = Message.objects.create(user_id=update.effective_user.id,
                                 message_json=json.dumps(update.message.to_dict(), ensure_ascii=False, indent=4))
    path = reverse(f'bots:{update.telegram_bot_pk}:inspector', kwargs={'pk': msg.pk})
    update.message.reply_text(f'https://{settings.WEBHOOK_DOMAIN}{path}')


def setup(dispatcher):
    dispatcher.add_handler(MessageHandler(Filters.all, inspector))
    return dispatcher
