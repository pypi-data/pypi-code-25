import hashlib

from django.conf import settings

from bomojo import settings as defaults


def get_avatar_url(email, size=None, default=None):
    email = email.lower()
    size = size or getattr(settings, 'DEFAULT_AVATAR_SIZE',
                           defaults.DEFAULT_AVATAR_SIZE)
    default = default or getattr(settings, 'DEFAULT_AVATAR_STYLE',
                                 defaults.DEFAULT_AVATAR_STYLE)

    digest = hashlib.new('md5', email.encode('utf-8')).hexdigest()
    return 'https://gravatar.com/avatar/%(digest)s?size=%(size)d&d=%(default)s' % {
        'digest': digest,
        'size': size,
        'default': default
    }
