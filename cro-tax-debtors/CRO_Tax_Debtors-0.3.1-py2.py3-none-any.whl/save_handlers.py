from slugify import slugify
from progress.bar import Bar
from db_transfer import Transfer


class RedisTransfer(Transfer):

    def __init__(self, prefix, namespace, host, port, db):
        super().__init__(prefix=str(prefix), namespace=namespace, adapter_name='redis')

        self.set_env('HOST', host)
        self.set_env('PORT', port)
        self.set_env('DB', db)


class Handler:

    _connection = {}

    def __init__(self, category_data):
        self._category_data = category_data

    @property
    def connection(self):
        key = 'debtors:' + self._category_data['namespace']
        if key not in self._connection:
            self._connection[key] = self._handler_connection()

        return self._connection[key]


class RedisHandler(Handler):

    def _handler_connection(self):
        return RedisTransfer('debtors',
                             self._category_data['namespace'],
                             **self._category_data['connection'])

    def save(self, data):
        item = slugify(data[self._category_data['item']])
        with self.connection as conn:
            del conn[item]
            conn[item] = data

        return data[self._category_data['item']], data[self._category_data['debt_key']]

    def find(self, name):
        data = self.connection[slugify(name)]
        if data:
            return [dict(data), ]
        else:
            return []

    def find_by_key(self, name):
        name = slugify(name)
        for key in self.connection.keys():
            if name in key:
                yield dict(self.connection[key])

    def delete(self):
        keys = self.connection.keys()
        bar = Bar('Deleting "' + self._category_data['title'] + '" from redis', max=len(keys))
        for key in keys:
            del self.connection[key]
            bar.next()
