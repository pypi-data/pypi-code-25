import da_ponz.utilities.logging_tools as logging_tools
import sqlalchemy
import time


def create_engine(settings):
    protocol = settings['protocol']
    user = settings['user']
    password = settings['password']
    host = settings['host']
    dbname = settings['dbname']
    engine = sqlalchemy.create_engine(protocol + '://' + user + ':' + password + '@' + host + '/' + dbname,
                                      pool_recycle=5)

    return engine


def get_table(engine, logger, table_name):
    attempts = 5

    for i in range(attempts):
        try:
            engine.connect()

        except sqlalchemy.exc.DatabaseError:
            message = 'The database is not currently available. This is attempt {} of {}.'.format(i + 1, attempts)
            logging_tools.log_event('error', logger, message)
            time.sleep(5)

        else:
            metadata = sqlalchemy.MetaData(bind=engine)
            table = sqlalchemy.Table(table_name, metadata, autoload=True, autoload_with=engine)
            return table


def insert_data(engine, table, values):
    query = sqlalchemy.insert(table).values(values)

    try:
        query_result = engine.execute(query)

    except sqlalchemy.exc.IntegrityError:
        result = {'result': 'error',
                  'message': 'The data was not inserted because it duplicated existing rows.'}

    else:
        primary_keys = query_result.inserted_primary_key

        if len(primary_keys) == 1:
            result = {'result': 'info',
                      'message': 'Data inserted into the {} table with primary key {}.'.
                          format(table.description, primary_keys[0])}

        else:
            result = {'result': 'info',
                      'message': 'Data inserted into the {} table with primary keys {} and {}.'.
                          format(table.description, primary_keys[0], primary_keys[1])}

    return result


def select_data(column_list, engine, select_from, where, limit=None, order=None):
    if order:
        direction = getattr(sqlalchemy, order['direction'])
        order = direction(order['field'])

    select = [getattr(select_from.c, column) for column in column_list]
    where = list(where)
    query = sqlalchemy.select(select).select_from(select_from).where(sqlalchemy.and_(*where)).order_by(order). \
        limit(limit)
    results = engine.execute(query)

    return results.fetchall()
