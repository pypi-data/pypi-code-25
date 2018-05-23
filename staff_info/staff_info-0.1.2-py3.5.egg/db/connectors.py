import mysql.connector
from mysql.connector import errorcode
from tkinter.messagebox import askokcancel, showerror


class MySQLConnector:

    def __init__(self, **credentials):
        self.credentials = credentials
        self.last_row_id = None
        # self.connection = None

    @property
    def connection(self):
        cnx = None
        try:
            cnx = mysql.connector.connect(**self.credentials)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Wrong username/passwrod credential")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        return cnx

    def execute_sql(self, sql, *params, change=True):
        """
        Execute raw sql with provided parameters
        :param sql: raw sql string;
        :param params: placeholders in sql query
        :param change: flag, that indicates whether query is select or make changes to DB
        :return: results of executed query
        """
        # print('Running execute sql')
        cnx = self.connection
        cursor = cnx.cursor()
        result = None
        print(sql, params)
        try:
            result = cursor.execute(sql, params)
        except mysql.connector.errors.DataError:
            showerror('Type error', 'Incorrect data type')
        else:
            if change:
                if askokcancel('SQL changes', 'Commit changes?'):
                    cnx.commit()
                else:
                    cnx.rollback()
            elif cursor.with_rows:
                result = cursor.fetchall()
            self.last_row_id = cursor.lastrowid
            cursor.close()
        return result

    def execute_sql_in_transaction(self, *sql):
        cnx = self.connection
        cnx.start_transaction()
        cursor = cnx.cursor()
        try:
            for sql_row in sql:
                print(sql_row[0], sql_row[1])
                cursor.execute(sql_row[0], sql_row[1])
        except mysql.connector.errors.DataError:
            showerror('Type error', 'Incorrect data type')
        else:
            if askokcancel('SQL changes', 'Commit changes?'):
                cnx.commit()
            else:
                cnx.rollback()

    def close(self):
        self.connection.close()


def connection_factory(db_type, **credentials):
    if db_type == ('mysql'):
        connector = MySQLConnector
    else:
        raise ValueError('Connector for DB Type {} not implemented yet'.format(db_type))
    return connector(**credentials)










