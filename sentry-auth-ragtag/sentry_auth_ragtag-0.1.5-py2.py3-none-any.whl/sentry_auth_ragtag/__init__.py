from __future__ import absolute_import

from sentry.auth import register

from .provider import RagtagOAuth2Provider

register('ragtag', RagtagOAuth2Provider)
