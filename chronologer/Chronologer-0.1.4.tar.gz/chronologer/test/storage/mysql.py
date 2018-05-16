import decimal
import logging
import unittest
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse

import cherrypy

from .. import setUpModule  # @UnusedImport
from ...storage import mysql


class TestMysqlStorage(unittest.TestCase):

  all = {
    'level' : logging.DEBUG,
    'date'  : (None, None),
    'name'  : None,
    'query' : None
  }


  def setUp(self):
    self.testee = mysql.Storage(urlparse(cherrypy.config['storage']['dsn']))

    self.testee._db.cursor().execute('BEGIN')

  def tearDown(self):
    self.testee._db.cursor().execute('ROLLBACK')

  def testRecord(self):
    self.assertEqual(0, self.testee.count(self.all))

    now = datetime.utcnow().replace(tzinfo = timezone.utc, microsecond = 0)
    self.testee.record('some.test', now.timestamp(), logging.INFO,
      'The Realm of Shades', {'foo': [{'bar': -1}]})

    self.assertEqual(1, self.testee.count(self.all))

    actualRangeItem = self.testee.range(0, 0, self.all)[0]
    self.assertGreater(actualRangeItem['id'], 0)
    self.assertEqual('some.test', actualRangeItem['name'])
    self.assertEqual(logging.INFO, actualRangeItem['level'])
    self.assertEqual('The Realm of Shades', actualRangeItem['message'])
    self.assertEqual(now, actualRangeItem['ts'])

    actualItem = self.testee.get(actualRangeItem['id'])
    self.assertEqual(actualRangeItem['id'], actualItem['id'])
    self.assertEqual('some.test', actualItem['name'])
    self.assertEqual(logging.INFO, actualItem['level'])
    self.assertEqual(now, actualItem['ts'])
    self.assertEqual('The Realm of Shades', actualItem['message'])
    self.assertEqual({'foo': [{'bar': -1}]}, actualItem['logrec'])

  def testGet(self):
    now = datetime.utcnow().replace(tzinfo = timezone.utc, microsecond = 0)
    rec = {
      'int': 26,
      'float': 0.1,
      'decimal': decimal.Decimal('0.1'),
      'list': list(range(4)),
      'dict': dict(zip(range(4), range(3, -1, -1))),
      'none': None,
      'object': object()
    }
    id = self.testee.record('some.test', now.timestamp(), logging.INFO, None, rec)

    actual = self.testee.get(id)['logrec']
    self.assertEqual(26, actual['int'])
    self.assertEqual(0.1, actual['float'])
    self.assertEqual('0.1', actual['decimal'])
    self.assertEqual([0, 1, 2, 3], actual['list'])
    self.assertEqual({'0': 3, '1': 2, '2': 1, '3': 0}, actual['dict'])
    self.assertEqual(None, actual['none'])
    self.assertTrue(actual['object'].startswith('<object object at'))

  def testCount(self):
    self.assertEqual(0, self.testee.count(self.all))

    now = datetime.now(timezone.utc).replace(microsecond = 0)
    self.testee.record('some.test', now.timestamp(), logging.INFO,
      'The Realm of Shades', {'key': [{'a': 1}, {'b': 2}]})
    self.testee.record('something.test', now.timestamp(), logging.WARN,
      'The Realm of Shades', {'key': [{'a': 1}]})

    self.assertEqual(2, self.testee.count(self.all))

    self.assertEqual(0, self.testee.count(dict(self.all, level = logging.ERROR)))
    self.assertEqual(1, self.testee.count(dict(self.all, level = logging.WARN)))
    self.assertEqual(2, self.testee.count(dict(self.all, level = logging.INFO)))

    self.assertEqual(0, self.testee.count(dict(self.all,
      date = (now - timedelta(seconds = 10), now - timedelta(seconds = 5)))))
    self.assertEqual(0, self.testee.count(dict(self.all, level = logging.INFO,
      date = (now - timedelta(seconds = 10), now - timedelta(seconds = 5)))))
    self.assertEqual(2, self.testee.count(dict(self.all, level = logging.INFO,
      date = (now - timedelta(seconds = 10), now + timedelta(seconds = 5)))))

    self.assertEqual(0, self.testee.count(dict(self.all, name = 'foo')))
    self.assertEqual(1, self.testee.count(dict(self.all, name = 'some.')))
    self.assertEqual(1, self.testee.count(dict(self.all, name = 'something')))
    self.assertEqual(2, self.testee.count(dict(self.all, name = 'some, something')))
    self.assertEqual(2, self.testee.count(dict(self.all, name = 'so')))

    self.assertEqual(2, self.testee.count(dict(self.all, query = 'logrec->"$.key[0].a" = 1')))
    self.assertEqual(1, self.testee.count(dict(self.all, query = 'logrec->"$.key[1].b" = 2')))

    self.assertEqual(1, self.testee.count(dict(self.all,
      query = 'logrec->>"$.key[1].b" = 2',
      level = logging.INFO,
      date = (now - timedelta(seconds = 10), now + timedelta(seconds = 5))
    )))

  def testCountHistogram(self):
    now = datetime(2017, 6, 17, 23, 14, 37, tzinfo = timezone.utc)

    for i in range(16):
      self.testee.record('something.test', (now + timedelta(minutes = i * 5)).timestamp(),
        logging.WARN, 'Fela the Congueror', {'a': 1})

    actual = self.testee.count(self.all, group = True)
    self.assertEqual((
      (datetime(2017, 6, 17, 23, 0,  tzinfo = timezone.utc), 1),
      (datetime(2017, 6, 17, 23, 15, tzinfo = timezone.utc), 3),
      (datetime(2017, 6, 17, 23, 30, tzinfo = timezone.utc), 3),
      (datetime(2017, 6, 17, 23, 45, tzinfo = timezone.utc), 3),
      (datetime(2017, 6, 18, 0,  0,  tzinfo = timezone.utc), 3),
      (datetime(2017, 6, 18, 0,  15, tzinfo = timezone.utc), 3),
    ), actual)

    actual = self.testee.count(
      dict(self.all, date=(now + timedelta(minutes = 59), None), query = 'logrec->>"$.a" = 1'),
      group = True)
    self.assertEqual((
      (datetime(2017, 6, 18, 0,  0,  tzinfo = timezone.utc), 1),
      (datetime(2017, 6, 18, 0,  15, tzinfo = timezone.utc), 3),
    ), actual)

  def testRange(self):
    now = datetime.utcnow().replace(tzinfo = timezone.utc, microsecond = 0)
    self.testee.record('some.test', now.timestamp(), logging.INFO,
      'The Realm of Shades', {'key': [{'a': 1}, {'b': 2}]})
    self.testee.record('something.test', now.timestamp(), logging.WARN,
      'The Realm of Shades', {'key': [{'a': 1}]})

    actual = self.testee.range(0, 1, self.all)
    self.assertEqual(2, len(actual))
    self.assertGreater(actual[0]['id'], actual[1]['id'])
    [r.pop('id') for r in actual]
    self.assertEqual((
      {'level': 30, 'name': 'something.test', 'ts': now, 'message': 'The Realm of Shades'},
      {'level': 20, 'name': 'some.test', 'ts': now, 'message': 'The Realm of Shades'}
    ), actual)

    actual = self.testee.range(0, 0, self.all)
    self.assertEqual(1, len(actual))
    self.assertEqual('something.test', actual[0]['name'])

    actual = self.testee.range(1, 1, self.all)
    self.assertEqual(1, len(actual))
    self.assertEqual('some.test', actual[0]['name'])

    actual = self.testee.range(1, 0, self.all)
    self.assertEqual((), actual)

    actual = self.testee.range(0, 0, dict(self.all,
      query = 'logrec->>"$.key[1].b" = 2',
      level = logging.INFO,
      date = (now - timedelta(seconds = 10), now + timedelta(seconds = 5))
    ))
    self.assertEqual(1, len(actual))
    self.assertEqual('some.test', actual[0]['name'])

  def testReconnect(self):
    # suicide
    with self.assertRaises(mysql.connections.OperationalError) as ctx:
      self.testee._db.kill(self.testee._db.thread_id())
    self.assertEqual(str(ctx.exception), "(1317, 'Query execution was interrupted')")

    self.testee._db.cursor().execute('BEGIN')

    now = datetime.utcnow().replace(tzinfo = timezone.utc, microsecond = 0)
    self.testee.record('some.test', now.timestamp(), logging.INFO, None, None)
    self.assertEqual(1, self.testee.count(self.all))

