from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import Signal
from .utils import (extract_payload_from_command, get_bot_model,
                    get_telegram_user_model, get_authorization_model)
from .services import get_user_from_storage, activate_user
from django.utils.translation import ugettext_lazy as _


User = get_user_model()
Bot = get_bot_model()
TelegramUser = get_telegram_user_model()
Authentication = get_authorization_model()


receive_message = Signal(providing_args=['bot', 'chat_id', 'text', 'message'])

receive_command = Signal(providing_args=['bot', 'chat_id', 'command',
                                         'payload'])

receive_callback_query = Signal(providing_args=['bot_id', 'chat_id', 'data'])

subscribed_user = Signal(providing_args=['key', 'user', 'bot'])
unsubscribed_user = Signal(providing_args=['key', 'user', 'bot'])

activated_user = Signal(providing_args=['key', 'user', 'bot'])
deactivated_user = Signal(providing_args=['key', 'user', 'bot'])


@receiver(post_save, sender=User)
def create_bot_user(sender, instance, created, **kwargs):
    if created:
        TelegramUser.objects.create(user=instance)


@receiver(receive_command, sender=Bot)
def authentication_user(sender, **kwargs):
    if all(k in kwargs for k in ('bot', 'chat_id', 'command', 'payload')):
        command = kwargs['command']
        payload = kwargs['payload']
        bot = kwargs['bot']
        chat_id = kwargs['chat_id']
        #type = kwargs['type']

        if command == 'start' and payload:
            unique_code = extract_payload_from_command(payload)
            if unique_code:
                user = get_user_from_storage(unique_code)
                if user:
                    if not user.is_authorized:
                        activate_user(key=user.id, user=user, bot=bot)
                        #save_chat_id(chat_id, user)
                        reply = '''Hi, {}, the authentication
                                was successful!'''.format(user.user.username)
                    else:
                        reply = '{}, you are already authenticated'.format(
                            user.user.username)
                else:
                    reply = _('Unfortunately, I can ' +
                              'not authenticate you :(').encode('utf-8')
            else:
                reply = _('You can not be authenticated, ' +
                          'since a unique code is not '
                          'installed.').encode('utf-8')
            if isinstance(bot, Bot):
                bot.send_message(chat_id=chat_id, payload=reply)
