import json
import threading
from datetime import timezone, datetime

from MySQLdb import connect, constants, converters, cursors, connections


__all__ = 'Storage',


class ReconnectingDictCursor(cursors.DictCursor):
  '''Cursor that reconnects once on lost, timed out connection.
  As long as the package uses only simple auto-commit queries it's
  possible to follow simple retry approach on timeout.'''

  def execute(self, query, args = None):
    try:
      return super().execute(query, args)
    except connections.OperationalError as ex:
      # MySQL timeout errors:
      #   * (2006, 'MySQL server has gone away')
      #   * (2013, 'Lost connection to MySQL server during query')
      if ex.args[0] in (2006, 2013):
        try:
          # On Unix socket connection two pings as below are sufficient, unlike on TCP socket
          self.connection.ping(False)
        except connections.OperationalError:
          # See http://mysqlsimplequerybuilder.rtfd.io/en/latest/design.html#persistent-connection
          self.connection.ping(True)
          self.connection.ping(False)

        return super().execute(query, args)
      else:
        raise


class AbstractMysqlStorage:

  _local = threading.local()

  _config = None
  '''URL-parsed DSN'''


  def __init__(self, config):
    self._config = config

  @property
  def _db(self):
    if not hasattr(self._local, 'db'):
      self._local.db = self._createConnection()

    return self._local.db

  @staticmethod
  def _createConverters():
    result = converters.conversions.copy()

    def wrapDt(key):
      orig = result[key]
      def wrapper(s):
        r = orig(s)
        return r.replace(tzinfo = timezone.utc) if r else r

      result[key] = wrapper

    wrapDt(constants.FIELD_TYPE.DATETIME)
    wrapDt(constants.FIELD_TYPE.TIMESTAMP)

    # At the time of writing JSON type is not defined in the mysqlclient's module
    MYSQL_TYPE_JSON = 245
    result[MYSQL_TYPE_JSON] = json.loads

    return result

  def _createConnection(self):
    return connect(
      host         = self._config.hostname,
      user         = self._config.username,
      password     = self._config.password or '',
      database     = self._config.path.strip('/'),
      charset      = 'utf8mb4',
      conv         = self._createConverters(),
      autocommit   = True,
      cursorclass  = ReconnectingDictCursor
    )


class Storage(AbstractMysqlStorage):

  def _applyFilters(self, sql, values):
    nameSql = ''
    if values['name']:
      names   = map(str.strip, values['name'].split(','))
      parts   = ('name LIKE {0}'.format(self._db.literal(n + '%%')) for n in names)
      nameSql = 'AND ({0})'.format(' OR '.join(parts))

    return sql.format(
      name      = nameSql,
      level     = ' AND level >= %(level)s' if values['level'] else '',
      dateLeft  = ' AND ts >= %(left)s' if values['date'][0] else '',
      dateRight = ' AND ts <= %(right)s' if values['date'][1] else '',
      query     = ' AND ({0})'.format(values['query']) if values['query'] else ''
    )

  def _applyCountGroup(self, sql, group):
    dateGroup = groupBy = ''
    if group:
      dateGroup = ', FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(ts) / 900) * 900) `group`'
      groupBy = 'GROUP BY `group`'

    return sql.replace('{dateGroup}', dateGroup).replace('{groupBy}', groupBy)

  def count(self, filters, group = False):
    '''Return number of records matching given filters. If ``group`` is true
    return number per 15 minute intervals. 15 minute intervals allow grouping
    for arbitrary timezone. It could implemented on MySQL side as well with
    timezone-aware TIMESTAMP column and loaded timezone data. But this seems
    a hard requirement on storage.'''

    sql = '''
      SELECT COUNT(*) `count` {dateGroup}
      FROM record
      WHERE 1 {level} {name} {dateLeft} {dateRight} {query}
      {groupBy}
    '''
    sql = self._applyCountGroup(sql, group)

    cursor = self._db.cursor()
    cursor.execute(self._applyFilters(sql, filters), {
      'level' : filters['level'],
      'left'  : filters['date'][0],
      'right' : filters['date'][1],
    })

    if group:
      return tuple((r['group'], r['count']) for r in cursor.fetchall())
    else:
      return cursor.fetchone()['count']

  def range(self, left, right, filters):
    sql = '''
      SELECT record_id `id`, name, ts, level, message
      FROM record
      WHERE 1 {level} {name} {dateLeft} {dateRight} {query}
      ORDER BY record_id DESC
      LIMIT %(offset)s, %(limit)s
    '''

    cursor = self._db.cursor()
    cursor.execute(self._applyFilters(sql, filters), {
      'offset' : left,
      'limit'  : right - left + 1,
      'level'  : filters['level'],
      'left'   : filters['date'][0],
      'right'  : filters['date'][1],
    })

    return cursor.fetchall()

  def get(self, id):
    cursor = self._db.cursor()
    cursor.execute('''
      SELECT record_id `id`, name, ts, level, message, logrec
      FROM record
      WHERE record_id = %(id)s
    ''', {'id' : id})

    return cursor.fetchone()

  def record(self, name, ts, level, message, logrec):
    cursor = self._db.cursor()
    cursor.execute('''
      INSERT INTO `record`(`name`, `ts`, `level`, `message`, `logrec`)
      VALUES(%(name)s, %(ts)s, %(level)s, %(message)s, %(logrec)s)
    ''', {
      'name'    : name,
      'ts'      : datetime.utcfromtimestamp(ts).isoformat(' '),
      'level'   : level,
      'message' : message,
      'logrec'  : json.dumps(logrec, default = str)
    })
    return cursor.lastrowid

