""" Messages module """

from datetime import timedelta

# Kaira import
from kaira.signing import dumps as signing_dumps
from kaira.signing import loads as signing_loads


DEBUG = 10
INFO = 20
SUCCESS = 25
WARNING = 30
ERROR = 40

DEFAULT_TAGS = {
    DEBUG: 'debug',
    INFO: 'info',
    SUCCESS: 'success',
    WARNING: 'warning',
    ERROR: 'error',
}

DEFAULT_LEVELS = {
    'DEBUG': DEBUG,
    'INFO': INFO,
    'SUCCESS': SUCCESS,
    'WARNING': WARNING,
    'ERROR': ERROR,
}

LEVEL_TAGS = DEFAULT_LEVELS


class Message:
    """
    Represent an actual message that can be stored in any of the supported
    storage classes (typically session- or cookie-based) and rendered in a view
    or template.
    """

    def __init__(self, level, message, extra_tags=None):
        self.level = int(level)
        self.message = message
        self.extra_tags = extra_tags

    def _prepare(self):
        """
        Prepare the message for serialization by forcing the ``message``
        and ``extra_tags`` to str in case they are lazy translations.
        """
        self.message = str(self.message)
        self.extra_tags = str(self.extra_tags) if self.extra_tags is not None else None

    def __eq__(self, other):
        return isinstance(other, Message) and self.level == other.level and \
            self.message == other.message

    def __str__(self):
        return str(self.message)

    @property
    def tags(self):
        return ' '.join(tag for tag in [self.extra_tags, self.level_tag] if tag)

    @property
    def level_tag(self):
        return LEVEL_TAGS.get(self.level, '')


class BaseStorage:
    """
    This is the base backend for temporary message storage.
    This is not a complete class; to be a usable storage backend, it must be
    subclassed and the two methods ``_get`` and ``_store`` overridden.
    """

    def __init__(self, request, *args, **kwargs):
        self.request = request
        self._queued_messages = []
        self.used = False
        self.added_new = False
        super().__init__(*args, **kwargs)

    def __len__(self):
        return len(self._loaded_messages) + len(self._queued_messages)

    def __iter__(self):
        self.used = True
        if self._queued_messages:
            self._loaded_messages.extend(self._queued_messages)
            self._queued_messages = []
        return iter(self._loaded_messages)

    def __contains__(self, item):
        return item in self._loaded_messages or item in self._queued_messages

    @property
    def _loaded_messages(self):
        """
        Return a list of loaded messages, retrieving them first if they have
        not been loaded yet.
        """
        if not hasattr(self, '_loaded_data'):
            messages, all_retrieved = self._get()
            self._loaded_data = messages or []
        return self._loaded_data

    def _get(self, *args, **kwargs):
        """
        Retrieve a list of stored messages. Return a tuple of the messages
        and a flag indicating whether or not all the messages originally
        intended to be stored in this storage were, in fact, stored and
        retrieved; e.g., ``(messages, all_retrieved)``.
        **This method must be implemented by a subclass.**
        If it is possible to tell if the backend was not used (as opposed to
        just containing no messages) then ``None`` should be returned in
        place of ``messages``.
        """
        raise NotImplementedError('subclasses of BaseStorage must provide a _get() method')

    def _store(self, messages, response, *args, **kwargs):
        """
        Store a list of messages and return a list of any messages which could
        not be stored.
        One type of object must be able to be stored, ``Message``.
        **This method must be implemented by a subclass.**
        """
        raise NotImplementedError('subclasses of BaseStorage must provide a _store() method')

    def _prepare_messages(self, messages):
        """
        Prepare a list of messages for storage.
        """
        for message in messages:
            message._prepare()

    def update(self, response):
        """
        Store all unread messages.
        If the backend has yet to be iterated, store previously stored messages
        again. Otherwise, only store messages added after the last iteration.
        """
        self._prepare_messages(self._queued_messages)
        if self.used:
            return self._store(self._queued_messages, response)
        elif self.added_new:
            messages = self._loaded_messages + self._queued_messages
            return self._store(messages, response)

    def add(self, level, message, extra_tags=''):
        """
        Queue a message to be stored.
        The message is only queued if it contained something and its level is
        not less than the recording level (``self.level``).
        """
        if not message:
            return
        # Check that the message level is not less than the recording level.
        level = int(level)
        if level < self.level:
            return
        # Add the message.
        self.added_new = True
        message = Message(level, message, extra_tags=extra_tags)
        self._queued_messages.append(message)

    def _get_level(self):
        """
        Return the minimum recorded level.
        The default level is the ``MESSAGE_LEVEL`` setting. If this is
        not found, the ``INFO`` level is used.
        """
        if not hasattr(self, '_level'):
            self._level = INFO
        return self._level

    def _set_level(self, value=None):
        """
        Set a custom minimum recorded level.
        If set to ``None``, the default level will be used (see the
        ``_get_level`` method).
        """
        if value is None and hasattr(self, '_level'):
            del self._level
        else:
            self._level = int(value)

    level = property(_get_level, _set_level, _set_level)


class MessageStorage(BaseStorage):
    """
    Store messages in a cookie.
    """
    cookie_name = 'messages'
    # uwsgi's default configuration enforces a maximum size of 4kb for all the
    # HTTP headers. In order to leave some room for other cookies and headers,
    # restrict the session cookie to 1/2 of 4kb. See #18781.
    max_cookie_size = 2048
    not_finished = '__messagesnotfinished__'

    def __init__(self, request, *args, **kwargs):

        self.request = request
        self.cookies = kwargs.pop('cookies', None)
        options = kwargs.pop('options', None)
        if not options:
            options = {
                       'MESSAGES_COOKIE_DOMAIN': '',
                       'MESSAGES_COOKIE_SECURE': False,
                       'MESSAGES_COOKIE_HTTPONLY': True,
                       'MESSAGES_COOKIE_EXPIRE': 600,
                       'MESSAGES_COOKIE_PATH': '/',
                       'MESSAGES_COOKIE_NAME': 'kaira_message',
                       'MESSAGES_SECRET': b'APj00cpfa8Gx1SjnyLxwBBSQfnQ9DJYe0Cm',
                       'MESSAGES_TIME_LIMIT': timedelta(minutes=60)
                      }
        self.options = options
        self._queued_messages = []
        self.used = False
        self.added_new = False
        super().__init__(*args, **kwargs)

    def _get(self, *args, **kwargs):
        """
        Retrieve a list of messages from the messages cookie. If the
        not_finished sentinel value is found at the end of the message list,
        remove it and return a result indicating that not all messages were
        retrieved by this storage.
        """
        cookie_name = self.options['MESSAGES_COOKIE_NAME']
        data = self.request.cookies[cookie_name]
        messages = self._decode(data)
        all_retrieved = not (messages and messages[-1] == self.not_finished)
        if messages and not all_retrieved:
            # remove the sentinel value
            messages.pop()
        return messages, all_retrieved

    def _update_cookie(self, encoded_data, response):
        """
        Either set the cookie with the encoded data if there is any data to
        store, or delete the cookie.
        """
        if encoded_data:
            response.set_cookie(
                self.cookie_name, encoded_data,
                domain=settings.SESSION_COOKIE_DOMAIN,
                secure=settings.SESSION_COOKIE_SECURE or None,
                httponly=settings.SESSION_COOKIE_HTTPONLY or None,
                samesite=settings.SESSION_COOKIE_SAMESITE,
            )
        else:
            response.delete_cookie(self.cookie_name, domain=settings.SESSION_COOKIE_DOMAIN)

    def _store(self, messages, response, remove_oldest=True, *args, **kwargs):
        """
        Store the messages to a cookie and return a list of any messages which
        could not be stored.
        If the encoded data is larger than ``max_cookie_size``, remove
        messages until the data fits (these are the messages which are
        returned), and add the not_finished sentinel value to indicate as much.
        """
        unstored_messages = []
        encoded_data = self._encode(messages)
        if self.max_cookie_size:
            # data is going to be stored eventually by SimpleCookie, which
            # adds its own overhead, which we must account for.
            cookie = SimpleCookie()  # create outside the loop

            def stored_length(val):
                return len(cookie.value_encode(val)[1])

            while encoded_data and stored_length(encoded_data) > self.max_cookie_size:
                if remove_oldest:
                    unstored_messages.append(messages.pop(0))
                else:
                    unstored_messages.insert(0, messages.pop())
                encoded_data = self._encode(messages + [self.not_finished],
                                            encode_empty=unstored_messages)
        self._update_cookie(encoded_data, response)
        return unstored_messages

    def _encode(self, messages, encode_empty=False):
        """
        Return an encoded version of the messages list which can be stored as
        plain text.
        Since the data will be retrieved from the client-side, the encoded data
        also contains a hash to ensure that the data was not tampered with.
        """
        if messages or encode_empty:
            value = signing_dumps(messages,
                                  key=self.options['MESSAGES_SECRET'])
            return value

    def _decode(self, data):
        """
        Safely decode an encoded text stream back into a list of messages.
        If the encoded text stream contained an invalid hash or was in an
        invalid format, return None.
        """
        if not data:
            return None

        try:
            messages = signing_loads(data,
                                     key=self.options['MESSAGES_SECRET'],
                                     max_age=self.options['MESSAGES_TIME_LIMIT'])
        except:
            messages = None
            self.used = True

        return messages


# import datetime
# from datetime import timedelta
#
#
# class BaseFlashManager(object):
#     """Flash Manager"""
#
#     def __init__(self, request, msg, status, cookies=None, options=None):
#         """ Init """
#
#         self.request = request
#         self.cookies = cookies
#         self.msg = msg
#         self.status = status
#
#         if not options:
#             options = {
#                 'FLASH_COOKIE_DOMAIN': '',
#                 'FLASH_COOKIE_SECURE': False,
#                 'FLASH_COOKIE_HTTPONLY': True,
#                 'FLASH_COOKIE_EXPIRE': 600,
#                 'FLASH_COOKIE_PATH': '/',
#                 'FLASH_COOKIE_NAME': 'kaira_flash',
#                 'FLASH_SECRET': b'APj00cpfa8Gx1SjnyLxwBBSQfnQ9DJYe0Cm',
#                 'FLASH_TIME_LIMIT': timedelta(minutes=60)
#             }
#
#         self.options = options
#
#     def save(self):
#         """Save"""
#
#         expire_seconds = int(self.options['FLASH_COOKIE_EXPIRE'])
#         if expire_seconds > 0:
#             now = datetime.datetime.utcnow()
#             expires_cookie = now + datetime.timedelta(seconds=expire_seconds)
#         else:
#             expires_cookie = None
#
#         if not self.options['FLASH_COOKIE_DOMAIN'] or self.options['FLASH_COOKIE_DOMAIN'] == "":
#             domain = self.request.host.split(':')[0]
#         else:
#             domain = self.options['FLASH_COOKIE_DOMAIN']
#
#         cookies_options = {
#             'HTTP_COOKIE_DOMAIN': domain,
#             'HTTP_COOKIE_SECURE': self.options['FLASH_COOKIE_SECURE'],
#             'HTTP_COOKIE_HTTPONLY': self.options['FLASH_COOKIE_HTTPONLY']
#         }
#
#         cookie_name = self.options['FLASH_COOKIE_NAME']
#         time_limit = meta.csrf_options['FLASH_TIME_LIMIT']
#         csrf_secret = meta.csrf_options['CSRF_SECRET']
#
#         rand_code = None
#         if request.cookies:
#             if cookie_name in request.cookies:
#                 rand_code = request.cookies[cookie_name]
#
#         if not rand_code:
#             rand_code = sha1(os.urandom(64)).hexdigest()
#
#         if time_limit:
#             expires = (self.now() + time_limit).strftime(self.TIME_FORMAT)
#             csrf_build = '%s%s' % (rand_code, expires)
#         else:
#             expires = ''
#             csrf_build = rand_code
#
#         hmac_csrf = hmac.new(csrf_secret, csrf_build.encode('utf8'), digestmod=sha1)
#         value_csrf = '%s##%s' % (expires, hmac_csrf.hexdigest())
#
#         cookies = meta.cookies
#         if not cookies:
#             cookies = CookieManager(options=cookies_options)
#
#         cookies[cookie_name] = rand_code
#         cookies[cookie_name].path = meta.csrf_options['CSRF_COOKIE_PATH']
#         cookies[cookie_name].expires = expires_cookie
#
#         meta.cookies = cookies
