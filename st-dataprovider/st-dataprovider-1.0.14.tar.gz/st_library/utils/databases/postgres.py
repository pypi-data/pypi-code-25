import psycopg2

from st_library.utils.generics.connectors import ConnectorContainer


class Postgres(object):
    def __init__(self, name, host, port, username, password):
        self._name = name
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        # TODO: uses_google_sql
        self._conn = psycopg2.connect(database=self._name,
                                      user=self._username,
                                      password=self._password,
                                      host=self._host, port=self._port)

    def __repr__(self):
        return '<Postgres db "{}">'.format(self._name)

    @property
    def name(self):
        return self._name

    @property
    def conn(self):
        return self._conn


class PostgresContainer(ConnectorContainer):
    def _do_initialize_data(self):
        assert not len(self._list)

        params = self._fetch_param_dict([
            'psql_host', 'psql_name', 'psql_username', 'psql_password', 'psql_port'
        ])

        list_of_servers_params = [params]

        for server in list_of_servers_params:
            obj = Postgres(server['psql_name'], server['psql_host'],
                           int(server['psql_port']), server['psql_username'],
                           server['psql_password'])
            self._list.append(obj)
            self._dict[obj.name] = obj

    def _get_bool_uses_google_sql(self, raw_uses_google_sql):
        if raw_uses_google_sql == '1':
            return True
        return False
