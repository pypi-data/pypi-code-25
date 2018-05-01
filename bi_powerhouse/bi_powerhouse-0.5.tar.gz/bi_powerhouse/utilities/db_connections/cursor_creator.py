# -*- coding: utf-8 -*-

"""Creates a cursor for the designated DB engine"""

import pyodbc
import pymysql
import pg8000
import socket
import datetime

##########################################
##########################################
##########################################
##########################################


def create_cursor(engine, host, port, username, password, schema, autocommit=False):

    print(str(datetime.datetime.now())[:19] + ': Creating ' + engine + ' cursor for host ' + host + ' with user ' + username)

    ##########################################
    # for MySQL

    if engine == 'mysql':

        conn = pymysql.connect(host=host, port=port, user=username, passwd=password, db=schema, autocommit=autocommit,
                               connect_timeout=36000, local_infile=True, max_allowed_packet=16 * 1024, charset='utf8')

    ##########################################
    # for Redshift

    elif engine in ('redshift', 'postgresql'):

        conn = pg8000.connect(user=username, password=password, host=host, port=port, database=schema)

        conn._usock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        if autocommit:
            conn.autocommit = True

    ##########################################
    # for SQL Server

    elif engine == 'sqlserver':

        conn = pyodbc.connect(driver="{SQL Server}", server=host + ',' + str(port), database=schema,
                              uid=username, pwd=password, autocommit=autocommit)

    ##########################################
    # for invalid engine

    else:
        print(str(datetime.datetime.now())[:19] + ': Invalid engine name.')
        return None

    print(str(datetime.datetime.now())[:19] + ': Cursor created.')

    return conn.cursor()
