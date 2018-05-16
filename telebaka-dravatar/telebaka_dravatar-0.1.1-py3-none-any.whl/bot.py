from datetime import date
import io
import os
import tempfile
import uuid

from PIL import Image

from telegram import Bot, Update
from telegram.ext import MessageHandler, Filters, CommandHandler
from dynamic_preferences.registries import global_preferences_registry

from telebaka_dravatar.models import BotUser, BotUsage


global_preferences = global_preferences_registry.manager()


def save_user(user):
    BotUser.objects.update_or_create(user_id=user.id,
                                     defaults={
                                         'username': user.username,
                                         'name': f'{user.first_name} {user.last_name or ""}'.rstrip()
                                     })


def update_stats():
    usage, created = BotUsage.objects.get_or_create(date=date.today())
    usage.usages += 1
    usage.save()


def process_image(fp, message):
    update_stats()

    overlay = Image.open(global_preferences['dravatar__overlay_image']).convert('RGBA')
    im = Image.open(fp)  # type: Image.Image
    if im.size[0] != im.size[1]:
        return message.reply_text('Изображение не квадратное')
    resized_overlay = overlay.copy().resize(im.size, Image.ANTIALIAS)
    im.paste(resized_overlay, (0, 0), resized_overlay)
    im_fname = os.path.join(tempfile.gettempdir(), '{}.png'.format(uuid.uuid4().hex))
    im.save(im_fname)
    with open(im_fname, 'rb') as im_f:
        message.reply_document(im_f, caption='Готово!')


def start(bot: Bot, update: Update):
    save_user(update.effective_user)
    update.message.reply_text('Привет. Я помогу вам обновить ваш аватар. '
                              'Нажмите /generate чтобы начать. '
                              'Также вы можете загрузить любое квадратное изображение.')


def generate(bot: Bot, update: Update):
    save_user(update.effective_user)
    photos = bot.get_user_profile_photos(update.message.from_user.id)
    if not photos.photos:
        return update.message.reply_text('У вас нет аватарок')
    file_info = bot.get_file(photos.photos[0][-1].file_id)
    avatar = file_info.download_as_bytearray()
    process_image(io.BytesIO(avatar), update.message)


def generate_from_photo(bot: Bot, update: Update):
    save_user(update.effective_user)
    file_info = bot.get_file(update.message.photo[-1].file_id)
    avatar = file_info.download_as_bytearray()
    process_image(io.BytesIO(avatar), update.message)


def setup(dispatcher):
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', start))
    dispatcher.add_handler(CommandHandler('generate', generate))
    dispatcher.add_handler(MessageHandler(Filters.photo, generate_from_photo))
    return dispatcher
