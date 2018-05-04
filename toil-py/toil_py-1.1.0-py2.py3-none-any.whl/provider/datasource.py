# -*- coding: utf-8 -*-
"""
Provides access to data sources such as databases, files, rest etc.
See https://www.sqlalchemy.org/ for API details
"""
import logging
from sqlalchemy import create_engine
import toil.provider.base
import toil
import datetime

logger = logging.getLogger(__name__)


class DatasourceLib(toil.provider.base.BaseProvider):
    """
  The library for data sources.

  Properties :
    config: dict with configuration data
  """

    def __init__(self, toil, config):
        super(DatasourceLib, self).__init__(toil, config)

    def session(self, profile='default'):
        """
    Instantiate a data source provider.

    Args:
      profile (): a profile defined in config

    Returns:
      A data source provider.
    """

        if profile in self.config:
            self.configure_proxy()
            # dynamically load the class
            datasource_class = self._toil.load_class(self.config[profile]['provider'])
            # create an instance of class
            return datasource_class(self.config[profile])
        else:
            raise toil.CloudException(
                "profile '{profile}' not defined in config {config}".format(profile=profile, config=self.config))


class AlchemyMySQLDatasourceProvider(object):
    """
  Uses the Alchemy framework to access a mysql database.
  """

    @property
    def engine(self):
        return self._engine

    @engine.setter
    def engine(self, value):
        self._engine = value

    def __init__(self, config):
        self._engine = None
        self._config = config
        from sqlalchemy import MetaData
        self._meta = MetaData()
        connect_string = "{adapter}://{user}:{password}@{host}:{port}/{database}".format(
            adapter=config['adapter'],
            user=config['user'],
            password=config['password'],
            host=config['host'],
            port=config['port'],
            database=config['database']
        )
        echo_sql = False
        if 'log_level' in config and (config['log_level'] == 'debug'):
            echo_sql = True

        logger.debug(connect_string)
        self.engine = create_engine(connect_string, echo=echo_sql)

    def exec_sql(self, sql, **kwargs):
        """
    Execute a sql statement.  The statement is surrounded with a transaction.
    Yields the result to calling block.

    Args:
      sql (): the sql to execute
      **kwargs (): any arguments need in the sql statement

    Returns:
      sqlalchemy.engine.ResultProxy
    """
        from sqlalchemy.sql import text
        connection = self.engine.connect()
        connection.execution_options(autocommit=False)
        trans = connection.begin()
        try:
            stmt = text(sql)
            result = connection.execute(stmt, kwargs)
            yield result
            trans.commit()
        except Exception as ex:
            trans.rollback()
            connection.close()
            raise ex

    def exec_sql_query(self, sql, **kwargs):
        """
    Execute a sql query.  The statement is surrounded with a transaction.
    Loops over the result and yields each row to the calling block.

    Args:
      sql (): the sql to execute
      **kwargs (): any arguments need in the sql statement

    Returns:
     sqlalchemy.engine.RowProxy
    """
        from sqlalchemy.sql import text
        connection = self.engine.connect()
        connection.execution_options(autocommit=False)
        trans = connection.begin()
        try:
            stmt = text(sql)
            result = connection.execute(stmt, kwargs)
            for row in result:
                yield row
            trans.commit()
        except Exception as ex:
            trans.rollback()
            connection.close()
            raise ex

    def call_procedure(self, procedure_name, params=()):
        """
    Args:
      procedure_name (str): name of the stored procedure to execute
      params (): any parameters the procedure requires

    Returns:
      List
    """
        rows = []
        # sqlalchemy failed when handling resultset, so go native
        connection = self.engine.raw_connection()
        try:
            cursor = connection.cursor()
            cursor.callproc(procedure_name, params)

            for result in cursor.stored_results():
                rows = rows + result.fetchall()

            cursor.close()
            connection.commit()
            return rows
        finally:
            connection.close()

    def insert_ea_message_log(self, message_env, message_type, message_source, message_text):
        """
    Adds a message to the message log table which is used by applications to display user messages
    Args:
      message_env (str): environment
      message_type (str): type of message
      message_source (str): source such as class name, program name, etc.
      message_text (str): message to log

    Returns: None
    """
        from sqlalchemy import Table
        table = Table('ea_message_log', self._meta, autoload=True, autoload_with=self.engine)
        ins = table.insert().values([
            {'message_env': message_env, 'message_type': message_type,
             'message_source': message_source, 'message_text': message_text}
        ])

        connection = self.engine.connect()
        connection.execution_options(autocommit=False)
        trans = connection.begin()
        try:
            result = connection.execute(ins)
            logger.debug(result.inserted_primary_key)
            trans.commit()
        except Exception as ex:
            trans.rollback()
            connection.close()
            raise ex

    def insert_ea_log(self, log_message, log_time=datetime.datetime.utcnow(), log_location='.', log_type='DEBUG',
                      log_value='0', log_user='cloud', log_action='NONE', log_processed=0):
        """
    Add a meesage to the ea_lg table which is used for debugging and other processing purposes
    Args:
      log_message (): message to log
      log_time ():  the time in utc at the client
      log_location (): source such as class name, program name, etc.
      log_type (): debug, info, warn, error, etc.
      log_value (): a data value associated with log point
      log_user (): user name
      log_action (): action to perform when log is processed
      log_processed (): log is evaluated for execution purposes, set to 1 when complete
    Returns: None
    """
        from sqlalchemy import Table
        table = Table('ea_log', self._meta, autoload=True, autoload_with=self.engine)
        ins = table.insert().values([
            {'log_message': log_message,
             'log_time': log_time,
             'log_location': log_location,
             'log_type': log_type,
             'log_value': log_value,
             'log_user': log_user,
             'log_action': log_action,
             'log_processed': log_processed
             }
        ])
        connection = self.engine.connect()
        connection.execution_options(autocommit=False)
        trans = connection.begin()
        try:
            result = connection.execute(ins)
            logger.debug(result.inserted_primary_key)
            trans.commit()
        except Exception as ex:
            trans.rollback()
            connection.close()
            raise ex


class DataMapper(object):
    """
    Datamapper used in the framework.
    """

    @staticmethod
    def get_import_time():
        from datetime import datetime
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    def __init__(self, source_object):
        self.source_object = source_object

    def __getattr__(self, name):
        if self.source_object.has_key(name):
            return self.source_object[name]
        else:
            return ''

    def get(self, name):
        if self.source_object.has_key(name):
            return self.source_object[name]
        else:
            val = None
            eval_string = 'val = self.source_object' + name
            try:
                exec ('val = self.source_object' + name)
            except Exception as ex:
                logger.error(ex)
                return ''

            return val


class BaseDataTranser(object):
    """
    Provides data transfer
    """

    @property
    def total_count(self):
        return self._total_count

    @property
    def processed_count(self):
        return self._processed_count

    @property
    def compliant_count(self):
        return self._compliant_count

    @property
    def nested_compliant_count(self):
        return self._nested_compliant_count

    @property
    def violation_count(self):
        return self._violation_count

    @property
    def error_count(self):
        return self._error_count

    @property
    def group_size(self):
        return self._group_size

    @group_size.setter
    def group_size(self, value):
        self._group_size = value

    @property
    def eff_date(self):
        return self._eff_date

    @eff_date.setter
    def eff_date(self, value):
        self._eff_date = value

    @property
    def env(self):
        return self._env

    @env.setter
    def env(self, value):
        self._env = value

    def __init__(self):
        self._total_count = 0
        self._processed_count = 0
        self._compliant_count = 0
        self._nested_compliant_count = 0
        self._violation_count = 0
        self._group_size = 10
        self._error_count = 0
        self._compliant = []
        self._violation = []

        super(BaseDataTranser, self).__init__()

    def transfer(self, **kwargs):

        self.log_transfer_action(type(self).__name__ + ' transfer')

        self.pre_transfer()

        if kwargs.has_key('data'):
            self._transfer_data = kwargs.get('data')
        else:
            self._transfer_data = self.get_transfer_data()

        if kwargs.has_key('datasource_session'):
            self._datasource_session = kwargs.get('datasource_session')

        if self._transfer_data is not None:
            self._total_count = len(self._transfer_data)

            for transfer_record in self._transfer_data:
                try:
                    self._processed_count += 1
                    if self.is_compliant(transfer_record):

                        result = self.handle_compliant(transfer_record)
                        if isinstance(result, list):
                            self._compliant_count += 1
                            self._nested_compliant_count += len(result)
                            self._compliant.extend(self.handle_compliant(transfer_record))
                        else:
                            self._compliant_count += 1
                            self._compliant.append(self.handle_compliant(transfer_record))
                    else:
                        self._violation_count += 1
                        self._violation.append(self.handle_violation(transfer_record))
                except Exception as ex:
                    self._error_count += len(self._compliant)
                    logger.error(ex)
                    self.handle_error(transfer_record, ex)

                if (self._processed_count % self._group_size) == 0:
                    try:
                        self.transfer_group()
                    except Exception as ex:
                        self._error_count += len(self._compliant)
                        logger.error(ex)

            if len(self._compliant) > 0:
                try:
                    self.transfer_group()
                except Exception as ex:
                    self._error_count += 1
                    logger.error(ex)

        self.post_transfer()

    def transfer_group(self, *args, **kwargs):
        logger.debug('transfer_group')
        percent_complete = ((self._processed_count + 0.00) / (len(self._transfer_data) + 0.00)) * 100
        logger.info("processed:{processed} of {total} {percent}%".format(processed=self._processed_count,
                                                                         total=self._total_count,
                                                                         percent=percent_complete))

    def pre_transfer(self, *args, **kwargs):
        logger.debug('pre_transfer')

    def post_transfer(self, *args, **kwargs):
        logger.debug('post_transfer')

        transfer_results = \
            """
            {classname}
            env:{env}
            eff_date:{eff_date}
            total:{total}
            group_size:{group_size}
            processed:{processed}
            compliant:{compliant}
            nested_compliant: {nested_compliant}
            violation:{violation}
            error:{error}
            """.format(classname=self.__class__.__name__, env=self._env, eff_date=self._eff_date,
               total=self._total_count, processed=self._processed_count,
               compliant=self._compliant_count, nested_compliant=self._nested_compliant_count,
               violation=self._violation_count, group_size=self._group_size, error=self._error_count)
        logger.info(transfer_results)

    def is_compliant(self, transfer_record):
        logger.debug('is_compliant')
        return True

    def handle_compliant(self, transfer_record):
        logger.debug('handle_compliant')
        return transfer_record

    def handle_violation(self, transfer_record):
        logger.debug('handle_violation')
        return transfer_record

    def handle_error(self, transfer_record, error):
        logger.debug('handle_violation')
        return transfer_record

    def log_transfer_action(self, transfer_record):
        logger.debug('log_transfer_action')

    def get_transfer_data(self):
        logger.debug('get_transfer_data')
        return []

    def log_transfer_action(self, data):
        logger.debug('log_transfer_action')
