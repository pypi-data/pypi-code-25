# System Imports
from typing import Union, NoReturn

# Third-Party Imports

# Local Source Imports
from .context import Context


__author__ = 'H.D. "Chip" McCullough IV'

""" A Dictionary of values for creating a connection string. """
__settings__ = {
  'drivername': '',
  'host': '',
  'port': 0,
  'username': '',
  'password': '',
  'database': ''
}

""" A Dictionary of supported Dialects with supported Drivers. """
__dialects__ = {
    'postgresql': ['psycopg2', 'pg8000'],
    'mysql': ['mysqldb', 'mysqlconnector', 'oursql'],
    'oracle': ['cx_oracle'],
    'mssql': ['pyodbc', 'pymssql'],
    'sqllite': [],
}

def set_connection_string_settings(drivername: str, host: str, port: int, username: str, password: str, database: str) -> NoReturn:
    """
        Sets the values of the connection string settings.

    :param drivername: The Database driver (e.g. 'postgres', or 'postgres+psycopg2').
    :type drivername: str
    :param host: The URL/IP address of where the database is hosted (e.g. 'localhost').
    :type host: str
    :param port: The Port Number that the context is listening on (e.g. 5432)
    :type port: int
    :param username: The context user username (e.g. 'postgres')
    :type username: str
    :param password: The context user password (e.g. 'password')
    :type password: str
    :param database: The database name (e.g. 'my-cool-database')
    :type database: str
    """

    try:
        dialect, driver = drivername.split('+')
    except ValueError:
        dialect, driver = drivername, None

    if dialect in __dialects__.keys():
        if (driver is None) or ((driver is not None) and (driver in __dialects__.get(dialect))):
            __settings__.update({
                'drivername': drivername,
                'host': host,
                'port': port,
                'username': username,
                'password': password,
                'database': database
            })
        else:
            __errors = {
                'dialect': dialect,
                'driver': driver,
            }
            raise UnsupportedDriverException(
                message='The driver {driver} for dialect {dialect} is currently unsupported by Alchemist Stack.'
                    .format(driver=driver,
                            dialect=dialect),
                errors=__errors,
                dialect=dialect,
                driver=driver
            )
    else:
        __errors = {
            'dialect': dialect,
            'driver': driver,
        }
        raise UnsupportedDialectException(
            message='The dialect {dialect} is currently unsupported by Alchemist Stack.'
                .format(dialect=dialect),
            errors=__errors,
            dialect=dialect,
            driver=driver
        )

def create_context(*args, **kwargs) -> Context:
    return Context(settings=__settings__, *args, **kwargs)

class UnsupportedDialectException(Exception):
    """ Unsupported Dialect """

    def __init__(self, message: str, errors: dict, dialect: str, driver: str = None, *args):
        super().__init__(message, *args)
        self.__errors: dict = errors
        self.__dialect: str = dialect
        self.__driver: str = driver

    @property
    def errors(self) -> dict:
        return self.__errors

    @property
    def dialect(self) -> str:
        return self.__dialect

    @property
    def driver(self) -> Union[str, None]:
        return self.__driver

class UnsupportedDriverException(Exception):
    """ Unsupported Driver """

    def __init__(self, message: str, errors: dict, dialect: str, driver: str = None, *args):
        super().__init__(message, *args)
        self.__errors: dict = errors
        self.__dialect: str = dialect
        self.__driver: str = driver

    @property
    def errors(self) -> dict:
        return self.__errors

    @property
    def dialect(self) -> str:
        return self.__dialect

    @property
    def driver(self) -> Union[str, None]:
        return self.__driver