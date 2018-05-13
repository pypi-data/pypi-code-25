
import collections
from copy import copy
import itertools


class TransformedDict(collections.MutableMapping):
    """A dictionary that applies an arbitrary key-altering
       function before accessing the keys"""

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        return key


def FlatDict(ordered=False, case_sensative=True, separator='.'):
    if ordered:
        basetype = collections.OrderedDict
    else:
        basetype = dict

    class _FlatDict(collections.MutableMapping):
        def __init__(self, *args, **kwargs):
            store = basetype(*args, **kwargs)
            self.store = self.__flat__(store)

        def __flat__(self, map_, kpath=''):
            ''' Flattens key in hierarchical dictionary.

            if kpath is provided new map will be returned.
            Otherwise, flat keys will be created within map_

            Arga:
                map_: map to flatten
                kpath: 
            '''
            nmap = basetype()

            prefix = "{}{}".format(kpath, separator) if kpath else ""
            for k, v in list(map_.items()):
                tk = self.__keytransform__(k)
                if isinstance(v, collections.Mapping):
                    fv = self.__flat__(v, kpath="{}{}".format(prefix, tk))
                    nmap.update(fv)
                else:
                    nmap["{}{}".format(prefix, tk)] = v
            return nmap

        def __keytransform__(self, key):
            if not case_sensative:
                if isinstance(key, str):
                    key = key.lower()
                elif isinstance(key, collections.Iterable):
                    key = type(key)(map(lambda x: x.lower(), key))

            if not isinstance(key, str) and isinstance(key, collections.Iterable):
                key = separator.join(key)
            return key

        def __getitem__(self, key):
            key = self.__keytransform__(key)
            return self.store.__getitem__(key)

        def __setitem__(self, key, value):
            key = self.__keytransform__(key)
            if isinstance(value, collections.Mapping):
                value = self.__flat__(value, kpath=key)
                self.store.update(value)
                return
            self.store.__setitem__(key, value)

        def __delitem__(self, key):
            del self.store[self.__keytransform__(key)]

        def __iter__(self):
            return iter(self.store)

        def __len__(self):
            return len(self.store)

        def __repr__(self):
            return repr(self.store)

        def __str__(self):
            return str(self.store)

        def __copy__(self):
            return type(self)(self.store)

        def copy(self):
            return self.__copy__()

        def update(self, iter_):
            if isinstance(iter_, collections.Mapping):
                iter_ = iter_.items()
            for k, v in iter_:
                self.__setitem__(k, v)

        def asdict(self):
            return self.store

        def _unflat(self, store=None):

            if not store:
                store = self.store

            keyitems = []
            valitems = []
            for k, v in store.items():
                kpath, _, key = k.partition(separator)
                if key:
                    keyitems.append((kpath, (key, v)))
                else:
                    valitems.append((kpath, v))

            keyfunc = lambda x: x[0]
            data = sorted(keyitems, key=keyfunc)
            store = basetype()
            for k, g in itertools.groupby(data, keyfunc):
                subdict = dict([v for _, v in g])
                store[k] = self._unflat(subdict)

            store.update(dict(valitems))
            return store

        def unflat(self):
            ''' Returns self as hierarchical dict of self.store
            '''
            return self._unflat()

    return _FlatDict


def ComplexDict(ordered=False, case_sensative=True):
    if ordered:
        base = collections.OrderedDict
    else:
        base = dict

    class _ComplexDict(base):
        def __keytransform__(self, key):
            if not case_sensative:
                if isinstance(key, str):
                    key = key.lower()
                elif isinstance(key, collections.Iterable):
                    key = type(key)(map(lambda x: x.lower(), key))
            return key

        def __getitem__(self, key):
            if not case_sensative:
                key = key.lower()
            return self[key]

        def __setitem__(self, key, value):
            if not case_sensative:
                key = key.lower()
            self[key] = value

        def flat(self):
            return 

    return _ComplexDict


if __name__ == '__main__':
    import pprint
    from itertools import combinations

    d = { 'LONLYITEM': 'JUSTME',
         "EVENTOR": {
            "DATABASES": {
                "default": {
                    "dialect": "sqlite",
                    "query": {
                        "cache": "shared"
                    },
                },
                "sqfile00": {
                    "dialect": "sqlite",
                    "database": "/var/acrisel/sand/eventor/eventor/eventor/examples/example00.db"  
                },
                "pgdb1": {
                    "dialect": "postgresql",
                    "drivername" : "psycopg2",
                    "username": "arnon",
                    "password": "arnon42",
                    "host": "localhost",
                    "port": 5433,
                    "database": "pyground",
                    "schema": "play",
                },
                "pgdb2": {
                    "dialect": "postgresql",
                    "drivername" : "psycopg2",
                    "username": "arnon",
                    "password": "Chompi42",
                    "host": "192.168.1.70",
                    "port": 5432,
                    "database": "pyground",
                    "schema": "play",
                },
            }}}

    fd = FlatDict()(d)
    print(repr(fd))

    key = 'EVENTOR.DATABASEs.pgdb1.drivername'
    for ordered, case_sensative in set(combinations([True, False, True, False], 2)):
        print("ordered, case_sensative:", ordered, case_sensative)
        f = FlatDict(ordered=ordered, case_sensative=case_sensative, separator='.')(d)
        try:
            print(f[key])
        except KeyError:
            print('Missing:', key)

        f['A'] = {'1': 2, '2': 3}
        f.update({'B': {'1': 2, '2': 3}})
        pprint.pprint(f['B.1'])

    print('LONLYITEM:', f['LONLYITEM'])
    pprint.pprint(f.unflat())    