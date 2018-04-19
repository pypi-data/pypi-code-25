# -*- coding: utf-8 -*-

import requests
from robot.api import logger
from robot.utils import ConnectionCache


class RequestConnection(object):
    """
    Settings for creating connection to Couchbase via HTTP
    """

    def __init__(self, host, port, username, password, timeout):
        """
        Initialization.\n

        *Args:*\n
            _host_ - hostname;\n
            _port_ - port address;\n
            _username_ - username;\n
            _password_ - user password;\n
            _timeout_ - connection attempt timeout;\n

        """
        self.host = host
        self.port = port
        self.url = 'http://{host}:{port}'.format(host=host, port=port)
        self.auth = (username, password)
        self.timeout = timeout

    def close(self):
        """Close connection"""
        pass


class CouchbaseManager(object):
    """
    Library for managing Couchbase server.

    Based on:
    [ http://docs.couchbase.com/couchbase-manual-2.5/cb-rest-api/ | Using the REST API ]

    == Dependencies ==
        | robot framework | http://robotframework.org |

    == Example ==
        | *Settings* | *Value* |
        | Library    | CouchbaseManager |
        | Library    | Collections |

        | *Test Cases* | *Action* | *Argument* | *Argument* | *Argument* | *Argument* | *Argument* |
        | Simple |
        |    | Connect To Couchbase | my_host_name | 8091 | administrator | administrator | alias=couchbase |
        |    | ${overview}= | Overview |
        |    | Log Dictionary | ${overview} |
        |    | Close All Couchbase Connections |
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, pool='default'):
        """
        Library initialization.\n
        Robot Framework ConnectionCache() class is prepared for working with concurrent connections.

        *Args*:\n
            _pool_: name for connection pool.
        """
        self._connection = None
        self.headers = {}
        self._cache = ConnectionCache()
        self.pool = pool

    def connect_to_couchbase(self, host, port, username='administrator',
                             password='administrator', timeout=15, alias=None):
        """
        Create connection to Couchbase server and set it as active connection.

        *Args:*\n
            _host_ - hostname;\n
            _port_ - port address;\n
            _username_ - username;\n
            _password_ - user password;\n
            _timeout_ - connection attempt timeout;\n
            _alias_ - connection alias;\n

        *Returns:*\n
            Index of the created connection.

        *Example:*\n
            | Connect To Couchbase | my_host_name | 8091 | administrator | administrator | alias=rmq |
        """

        port = int(port)
        timeout = int(timeout)
        logger.debug(
            'Connecting using : host={0}, port={1}, username={2}, '
            'password={3}, timeout={4}, alias={5} '
            .format(host, port, username, password, timeout, alias))

        self._connection = RequestConnection(host, port, username, password, timeout)
        return self._cache.register(self._connection, alias)

    def switch_couchbase_connection(self, index_or_alias):
        """
        Switch to another existing Couchbase connection using its index or alias.\n
        Connection alias is set in keyword [#Connect To Couchbase|Connect To Couchbase], which also returns connection index.

        *Args:*\n
            _index_or_alias_ - connection index or alias;

        *Returns:*\n
            Index of the previous connection.

        *Example:*\n
            | Connect To Couchbase | my_host_name_1 | 8091 | administrator | administrator | alias=couchbase1 |
            | Connect To Couchbase | my_host_name_2 | 8091 | administrator | administrator | alias=couchbase2 |
            | Switch Couchbase Connection | couchbase1 |
            | ${overview}= | Overview |
            | Switch Couchbase Connection | couchbase2 |
            | ${overview}= | Overview |
            | Close All Couchbase Connections |
        """

        old_index = self._cache.current_index
        self._connection = self._cache.switch(index_or_alias)
        return old_index

    def disconnect_from_couchbase(self):
        """
        Close active Couchbase connection.

        *Example:*\n
            | Connect To Couchbase | my_host_name | 8091 | administrator | administrator | alias=couchbase |
            | Disconnect From Couchbase |
        """

        logger.debug('Close connection with : host={0:s}, port={1:d}  '
                     .format(self._connection.host, self._connection.port))
        self._connection.close()

    def close_all_couchbase_connections(self):
        """
        Close all open Couchbase connections.\n
        You should not use [#Disconnect From Couchbase|Disconnect From Couchbase] and [#Close All Couchbase Connections|Close All Couchbase Connections]
        together.\n
        After executing this keyword connection indexes returned by opening new connections [#Connect To Couchbase |Connect To Couchbase]
        starts from 1.\n

        *Example:*\n
            | Connect To Couchbase | my_host_name | 8091 | administrator | administrator | alias=couchbase |
            | Close All Couchbase Connections |
        """

        self._connection = self._cache.close_all()

    def _prepare_request_headers(self, body=None):
        """
        Prepare headers for HTTP request.

        Args:*\n
            _body_: HTTP request body.\n

        *Returns:*\n
            Dictionary with HTTP request headers\n
        """
        headers = self.headers.copy()
        headers["Accept"] = "application/json"
        if body:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        return headers

    def overview(self):
        """
        Get overview info on Couchbase server.

        *Returns:*\n
            Dictionary with overview info.

        *Raises:*\n
            raise HTTPError if the HTTP request returned an unsuccessful status code.

        *Example:*\n
            | ${overview}=  |  Overview |
            | Log Dictionary  |  ${overview} |
            | ${version}=  |  Get From Dictionary | ${overview}  |  implementationVersion |
            =>\n
            | ${version} = 2.2.0-821-rel-enterprise
        """

        url = self._connection.url + '/pools/'
        response = requests.get(url, auth=self._connection.auth,
                                headers=self._prepare_request_headers(),
                                timeout=self._connection.timeout)
        response.raise_for_status()
        return response.json()

    def view_all_buckets(self):
        """
        Retrieve information on all buckets and their operations.

        *Returns:*\n
            List with buckets information

        *Raises:*\n
            raise HTTPError if the HTTP request returned an unsuccessful status code.

        *Example:*\n
            | ${buckets}=  |  View all buckets  |  default |
            | Log list  |  ${buckets} |
            =>\n
            | List length is 3 and it contains following items:
            | 0: {u'bucketType': u'membase', u'localRandomKeyUri'
            | ...
        """
        path = '/pools/{pool}/buckets'.format(pool=self.pool)
        response = requests.get(self._connection.url + path,
                                auth=self._connection.auth,
                                headers=self._prepare_request_headers(),
                                timeout=self._connection.timeout)
        response.raise_for_status()
        return response.json()

    def get_names_of_all_buckets(self):
        """
        Retrieve all bucket names for active pool.

        *Returns:*\n
            List with bucket names.

        *Example:*\n
            | ${names}=  |   Get names of all buckets  |  default |
            | Log list  |  ${names} |
            =>\n
            | 0: default
            | 1: ufm
            | 2: ufm_support
        """

        names = []
        data = self.view_all_buckets()
        for item in data:
            names.append(item['name'])
        return names

    def flush_bucket(self, bucket):
        """
        Flush specified bucket.

        *Args:*\n
            _bucket_ - bucket name;\n

        *Raises:*\n
            raise HTTPError if the HTTP request returned an unsuccessful status code.

        *Example:*\n
            | Flush bucket  |  default |

        """

        path = '/pools/{pool}/buckets/{bucket}/controller/doFlush'.format(pool=self.pool, bucket=bucket)
        response = requests.post(self._connection.url + path,
                                 auth=self._connection.auth,
                                 headers=self._prepare_request_headers(),
                                 timeout=self._connection.timeout)
        response.raise_for_status()

    def modify_bucket_parameters(self, bucket, **kwargs):
        """
        Modify bucket parameters.

        *Args:*\n
            _bucket_ - bucket name;\n
            _**kwargs_ - bucket parameters, parameter_name=value; parameter list can be found in
                         [http://docs.couchbase.com/couchbase-manual-2.5/cb-rest-api/#modifying-bucket-parameters| Couchbase doc]

        *Raises:*\n
            raise HTTPError if the HTTP request returned an unsuccessful status code.

        *Example:*\n
            | Modify bucket parameters  |  default  |  flushEnabled=1  |  ramQuotaMB=297 |
        """

        path = '/pools/{pool}/buckets/{bucket}'.format(pool=self.pool, bucket=bucket)
        response = requests.post(self._connection.url + path,
                                 auth=self._connection.auth,
                                 data=kwargs,
                                 headers=self._prepare_request_headers(body=kwargs),
                                 timeout=self._connection.timeout)
        response.raise_for_status()
