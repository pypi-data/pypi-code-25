# -*- coding: utf-8 -*-

import six

from datetime import datetime

from django.contrib.sessions.backends.base import SessionBase, CreateError
from django.utils import timezone

from django_restful import DoesNotExistError, RestfulApiError

from django_sae.models.session import SessionModel


class SessionStore(SessionBase):
    """
    Implements database session store.
    """

    def __init__(self, session_key=None):
        self._api = SessionModel()

        super(SessionStore, self).__init__(session_key)

    def load(self):
        """
        Loads the session data and returns a dictionary.
        """
        try:
            s = self._api.get_one(self.session_key)
            exprire_date = s['expire_date']

            if isinstance(exprire_date, six.string_types):
                exprire_date = datetime.strptime(
                    exprire_date[0:19].replace('T', ' '), '%Y-%m-%d %H:%M:%S')

            if exprire_date < datetime.now():
                raise DoesNotExistError
            return self.decode(s['session_data'])
        except DoesNotExistError:
            self.create()
            return {}

    def exists(self, session_key):
        """
        Returns True if the given session_key already exists.
        """
        return self._api.exists(session_key)

    def create(self):
        """
        Creates a new session instance. Guaranteed to create a new object with
        a unique key and will have saved the result once (with empty data)
        before the method returns.
        """
        while True:
            self._session_key = self._get_new_session_key()
            try:
                # Save immediately to ensure we have a unique entry in the
                # database.
                self.save(must_create=True)
            except CreateError:
                # Key wasn't unique. Try again.
                continue
            self.modified = True
            self._session_cache = {}
            return

    def save(self, must_create=False):
        """
        Saves the session data. If 'must_create' is True, a new session object
        is created (otherwise a CreateError exception is raised). Otherwise,
        save() can update an existing object with the same key.
        """
        obj = {'session_key': self._get_or_create_session_key(),
               'session_data': self.encode(self._get_session(no_load=must_create)),
               'expire_date': self.get_expiry_date()}
        try:
            if must_create:
                self._api.add(obj)
            else:
                self._api.exist_modify(obj)
        except RestfulApiError:
            if must_create:
                raise CreateError
            raise

    def delete(self, session_key=None):
        """
        Deletes the session data under this key. If the key is None, the
        current session key value is used.
        """
        if session_key is None:
            if self.session_key is None:
                return
            session_key = self.session_key

        self._api.delete(session_key)

    @classmethod
    def clear_expired(cls):
        """
        Remove expired sessions from the session store.

        If this operation isn't possible on a given backend, it should raise
        NotImplementedError. If it isn't necessary, because the backend has
        a built-in expiration mechanism, it should be a no-op.
        """

        api = SessionModel()
        api.clear_expired()
