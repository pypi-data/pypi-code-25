import logging
import time
from flask import Response
from google.cloud import datastore

_client = datastore.Client()
_logger = logging.getLogger('datastore-logger')


class DatastoreMessage(object):
    _keys = ['datetime', 'level', 'path', 'message']

    def __init__(self, message):
        if not isinstance(message, datastore.Entity):
            raise ValueError('DatastoreMessage must be type datastore.Entity')
        if len(set(self._keys) & set(message.keys())) < len(self._keys):
            raise ValueError('DatastoreMessage Entity must have keys: {0}'.format(self._keys))

        self.formatter = '%(datetime)s %(level)s %(path)s: %(message)s\n'
        self.entity = message

    def __repr__(self):
        return self.formatter % self.entity

    def __str__(self):
        return self.__repr__()


class DatastoreLog(object):
    def __init__(self, *key):
        """
        Args:
            *key: a spread of Entity key args. See:
            https://googlecloudplatform.github.io/google-cloud-python/latest/datastore/client.html#google.cloud.datastore.client.Client.key
        """
        self._key = _client.key(*key)
        self._log = _client.get(self._key)
        if self._log is None:
            raise ValueError('DatastoreLog Entity with Key "{0}" does not exist.'.format(key))

    @property
    def filename(self):
        return '{0}_{1}.log'.format(self._key.kind, self._key.id_or_name)

    def __iter__(self):
        query = _client.query(ancestor=self._key)
        query.kind = 'message'
        query.order = ['created']
        for message in query.fetch():
            if message.key.parent:
                yield DatastoreMessage(message)

    def __len__(self):
        query = _client.query(ancestor=self._key)
        query.keys_only()
        return len([x for x in query.fetch() if x.key.parent])

    def stream_response(self):
        def yield_chunks():
            for chunk in self:
                yield str(chunk)
        return Response(yield_chunks(), headers={
            'Content-Type': 'text/plain',
            'Content-Disposition': 'attachment; filename={0};'.format(self.filename)
        })

    def clear(self):
        def yield_chunks(keys):
            for i in xrange(0, len(keys), 500):
                yield keys[i:i + 500]

        query = _client.query(ancestor=self._key)
        query.kind = 'message'
        query.keys_only()

        # delete messages 500 at a time
        for chunk in yield_chunks([x.key for x in query.fetch()]):
            _client.delete_multi(chunk)

    def delete(self):
        def yield_chunks(keys):
            for i in xrange(0, len(keys), 500):
                yield keys[i:i + 500]

        query = _client.query(ancestor=self._key)
        query.keys_only()

        # delete messages 500 at a time
        for chunk in yield_chunks([x.key for x in query.fetch()]):
            _client.delete_multi(chunk)


class DatastoreLogHandler(logging.Handler):
    """
    A class which sends messages to Google Cloud Datastore
    """

    def __init__(self, *key):
        """
        Args:
            *key: a spread of Entity key args. See:
            https://googlecloudplatform.github.io/google-cloud-python/latest/datastore/client.html#google.cloud.datastore.client.Client.key
        """
        logging.Handler.__init__(self)

        self._key = _client.key(*key)
        self._log = _client.get(self._key)
        if not self._log:
            self._log = datastore.Entity(self._key)

        _client.put(self._log)

    def format_time(self, record):
        # sourced from logging.Formatter.formatTime
        ct = time.gmtime(record.created)
        t = time.strftime("%Y-%m-%d %H:%M:%S", ct)
        s = "%s,%03d" % (t, record.msecs)
        return s

    def format(self, record):
        # ensure default formatter
        self.setFormatter(logging.Formatter("%(message)s"))

        return {
            'datetime': self.format_time(record),
            'created': record.created,
            'level': record.levelname,
            'path': '%s:%s' % (record.pathname, record.lineno),
            'message': super(DatastoreLogHandler, self).format(record)
        }

    def emit(self, record):
        """
        Emit a record.
        """
        try:
            key = _client.key('message', parent=self._key)
            message = datastore.Entity(key, exclude_from_indexes=['message'])
            for k, v in self.format(record).iteritems():
                message[k] = v
            _client.put(message)
        except Exception:
            _logger.exception('Failed to log record: {0}'.format(record.__dict__))
            self.handleError(record)
