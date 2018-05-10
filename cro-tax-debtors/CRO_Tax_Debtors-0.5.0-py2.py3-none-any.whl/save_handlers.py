import ujson
from slugify import slugify
from progress.bar import Bar
from db_transfer import Transfer


class RedisTransfer(Transfer, object):

    def __init__(self, prefix, namespace, host, port, db):
        super(RedisTransfer, self).__init__(prefix=str(prefix), namespace=namespace, adapter_name='redis')

        self.set_env('HOST', host)
        self.set_env('PORT', port)
        self.set_env('DB', db)


class YamlFileTransfer(Transfer, object):

    def __init__(self, prefix, namespace, file_path):
        super(YamlFileTransfer, self).__init__(prefix=str(prefix), namespace=namespace, adapter_name='yaml')

        self.set_env('FILE_LOCAL', file_path)


class Handler(object):

    _connection = {}

    def __init__(self, category_data):
        self._category_data = category_data

    @property
    def connection(self):
        key = 'debtors:' + self._category_data['namespace']
        if key not in self._connection:
            self._connection[key] = self._handler_connection()

        return self._connection[key]

    def save(self, data):
        item = slugify(data[self._category_data['item']])

        del self.connection[item]
        self.connection[item] = self._dumps(data)

        return data[self._category_data['item']], data[self._category_data['debt_key']]

    def find(self, name):
        data = self.connection[slugify(name)]
        if data:
            return [self._loads(data), ]
        else:
            return []

    def find_by_key(self, name):
        name = slugify(name)
        for key in self.connection.keys():
            if name in key:
                yield self._loads(self.connection[key])

    def delete(self):
        keys = self.connection.keys()
        bar = Bar('Deleting "' + self._category_data['title'] + '" from redis', max=len(keys))
        for key in keys:
            del self.connection[key]
            bar.next()


class RedisHandler(Handler):

    def _handler_connection(self):
        return RedisTransfer('debtors',
                             self._category_data['namespace'],
                             **self._category_data['connection'])

    def _dumps(self, data):
        return dict(data)

    def _loads(self, data):
        return dict(data)


class YamlFileHandler(Handler):

    def _handler_connection(self):
        return YamlFileTransfer('debtors',
                                self._category_data['namespace'],
                                **self._category_data['connection'])

    def _dumps(self, data):
        return ujson.dumps(data)

    def _loads(self, data):
        return ujson.loads(data)
