import sys
import json
import types
import logging.handlers
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from unittest import mock

# CherryPy helper uses nose as runner, emulate for standard runner
sys.modules['nose'] = types.ModuleType('nose')
from cherrypy.test.helper import CPWebCase
import cherrypy

from . import setUpModule


delattr(CPWebCase, 'test_gc')

class TestController(CPWebCase):

  interactive = False

  maxDiff = None


  def setUp(self):
    # Proxy nose's setup
    self.setup_class()

  @classmethod
  def setup_server(cls):
    setUpModule()

  def tearDown(self):
    # Proxy nose's teardown
    self.teardown_class()


class TestApi(TestController):

  def setUp(self):
    super().setUp()

    def truncate():
      cherrypy.tree.apps['/api/v1/record'].storage._db.cursor().execute('TRUNCATE record')
    truncate()
    self.addCleanup(truncate)

  def testPostInfo(self):
    logrec = {
      'lineno'          : '10',
      'thread'          : '140550102431488',
      'levelno'         : '20',
      'msecs'           : '63.5066032409668',
      'levelname'       : 'INFO',
      'lisfor'          : 'lightfullness',
      'nested'          : "[{1: 2}, ('123', '234')]",
      'stack_info'      : 'None',
      'threadName'      : 'MainThread',
      'filename'        : 'log.py',
      'exc_text'        : 'None',
      'module'          : 'log',
      'relativeCreated' : '11.342048645019531',
      'msg'             : 'Band – %d, %s',
      'processName'     : 'MainProcess',
      'created'         : '1497106862.0635066',
      'funcName'        : 'info',
      'args'            : "(8, 'arg2')",
      'asctime'         : '2017-06-10 17:01:02,063',
      'exc_info'        : 'None',
      'message'         : 'Band – 8, arg2',
      'foo'             : 'bar',
      'process'         : '29799',
      'pathname'        : 'log.py',
      'name'            : 'test'
    }
    body = urlencode(logrec)
    headers = [
      ('content-type',   'application/x-www-form-urlencoded'),
      ('content-length', str(len(body)))
    ]

    self.getPage('/api/v1/record', method = 'post', body = body, headers = headers)
    self.assertStatus(201)
    id = int(self.body)

    self.getPage('/api/v1/record/{}'.format(id))
    self.assertStatus(200)
    self.assertHeader('Cache-Control', 'max-age=2600000')

    body = json.loads(self.body.decode())
    self.assertEqual({
      'level'   :  20,
      'ts'      : '2017-06-10 15:01:02.063507+00:00',
      'name'    : 'test',
      'message' : 'Band – 8, arg2',
      'id'      : id,
      'logrec'  : {
        'meta' : {
          'lineno'          : 10,
          'msecs'           : 63.5066032409668,
          'processName'     : 'MainProcess',
          'relativeCreated' : 11.342048645019531,
          'thread'          : 140550102431488,
          'filename'        : 'log.py',
          'msg'             : 'Band – %d, %s',
          'threadName'      : 'MainThread',
          'args'            : [8, 'arg2'],
          'module'          : 'log',
          'process'         : 29799,
          'funcName'        : 'info',
          'pathname'        : 'log.py',
          'stack_info'      : None
        },
        'data' : {
          'foo'    : 'bar',
          'lisfor' : 'lightfullness',
          'nested' : [{'1': 2}, ['123', '234']],
        }
      }
    }, body)

  def testPostError(self):
    logrec = {
      'lineno'          : '16',
      'thread'          : '140550102431488',
      'levelno'         : '40',
      'msecs'           : '97.82838821411133',
      'levelname'       : 'ERROR',
      'pathname'        : 'log.py',
      'stack_info'      : 'None',
      'threadName'      : 'MainThread',
      'filename'        : 'log.py',
      'module'          : 'log',
      'relativeCreated' : '45.66383361816406',
      'msg'             : 'Failure %s',
      'processName'     : 'MainProcess',
      'created'         : '1497106862.0978284',
      'funcName'        : 'error',
      'args'            : '(123,)',
      'asctime'         : '2017-06-10 17:01:02,097',
      'message'         : 'Failure 123',
      'process'         : '29799',
      'name'            : 'test',
      'exc_text'        : 'Traceback (most recent call last):\n'
        '  File "log.py", line 72, in <module>\n    1 / 0\n'
        'ZeroDivisionError: division by zero',
      'exc_info' : "(<class 'ZeroDivisionError'>, "
        "ZeroDivisionError('division by zero',), <traceback object at 0x7fd45c98b248>)",
    }
    body = urlencode(logrec)
    headers = [
      ('content-type',   'application/x-www-form-urlencoded'),
      ('content-length', str(len(body)))
    ]

    self.getPage('/api/v1/record', method = 'post', body = body, headers = headers)
    self.assertStatus(201)
    id = int(self.body)

    self.getPage('/api/v1/record/{}'.format(id))
    self.assertStatus(200)

    body = json.loads(self.body.decode())
    self.assertEqual({
      'level'   : 40,
      'name'    : 'test',
      'id'      : id,
      'message' : 'Failure 123',
      'ts'      : '2017-06-10 15:01:02.097828+00:00',
      'logrec'  : {
        'meta' : {
          'thread'          : 140550102431488,
          'process'         : 29799,
          'processName'     : 'MainProcess',
          'args'            : [123],
          'funcName'        : 'error',
          'lineno'          : 16,
          'filename'        : 'log.py',
          'threadName'      : 'MainThread',
          'msecs'           : 97.82838821411131,
          'module'          : 'log',
          'msg'             : 'Failure %s',
          'relativeCreated' : 45.66383361816406,
          'pathname'        : 'log.py',
          'stack_info'      : None,
        },
        'error' : {
          'exc_text' : 'Traceback (most recent call last):\n  '
            'File "log.py", line 72, in <module>\n    1 / 0\nZeroDivisionError: division by zero',
          'exc_info' : "(<class 'ZeroDivisionError'>, ZeroDivisionError('division by zero',), "
            "<traceback object at 0x7fd45c98b248>)",
        }
      },
    }, body)

  def testHttpHandler(self):
    logger = logging.getLogger('{}.testHttpHandler'.format(__name__))
    logger.propagate = False
    logger.level = logging.INFO
    logger.addHandler(logging.handlers.HTTPHandler(
      host   = 'localhost:{}'.format(self.PORT),
      url    = '/api/v1/record',
      method = 'POST'
    ))

    now = datetime.utcnow().replace(microsecond = 0)

    logger.info('Test', extra = {'lisfor': 'lighty'})

    self.getPage('/api/v1/record', method = 'HEAD')
    self.assertStatus(200)
    self.assertEqual(1, int(dict(self.headers)['X-Record-Count']))
    self.assertHeader('Cache-Control', 'no-cache')

    try:
      1 / 0
    except Exception:
      logger.exception('Failure', extra = {'lisfor': 'twiggy'})

    self.getPage('/api/v1/record', method = 'HEAD')
    self.assertStatus(200)
    self.assertEqual(2, int(dict(self.headers)['X-Record-Count']))

    self.getPage('/api/v1/record?level=30&name=chronologer', method = 'HEAD')
    self.assertStatus(200)
    self.assertEqual(1, int(dict(self.headers)['X-Record-Count']))

    self.getPage('/api/v1/record?left=0&right=1')
    self.assertStatus(200)
    actual = json.loads(self.body.decode())

    for item in actual:
      self.assertAlmostEqual(
        now,
        datetime.strptime(item.pop('ts').rsplit('+', 1)[0], '%Y-%m-%d %H:%M:%S.%f'),
        delta = timedelta(seconds = 1))

    self.assertEqual([{
      'name'    : 'chronologer.test.controller.testHttpHandler',
      'id'      : 2,
      'level'   : logging.ERROR,
      'message' : 'Failure'
    }, {
      'name'    : 'chronologer.test.controller.testHttpHandler',
      'id'      : 1,
      'level'   : logging.INFO,
      'message' : 'Test'
    }], actual)

    params = {
      'left'   : 0,
      'right'  : 0,
      'after'  : (now - timedelta(seconds = 5)).isoformat() + 'Z',
      'before' : (now + timedelta(seconds = 5)).isoformat() + 'Z',
      'name'   : 'chronologer',
      'level'  : logging.ERROR,
      'query'  : 'logrec->>"$.data.lisfor" = "twiggy"',
    }
    self.getPage('/api/v1/record?' + urlencode(params))
    self.assertStatus(200)
    self.assertHeader('Cache-Control', 'no-cache')
    actual = json.loads(self.body.decode())
    self.assertAlmostEqual(
      now,
      datetime.strptime(actual[0].pop('ts').rsplit('+', 1)[0], '%Y-%m-%d %H:%M:%S.%f'),
      delta = timedelta(seconds = 1))
    self.assertEqual([{
      'name'    : 'chronologer.test.controller.testHttpHandler',
      'id'      : 2,
      'level'   : logging.ERROR,
      'message' : 'Failure'
    }], actual)

  def testCountHistorgram(self):
    logger = logging.getLogger('{}.testCountHistorgram'.format(__name__))
    logger.propagate = False
    logger.level = logging.INFO
    logger.addHandler(logging.handlers.HTTPHandler(
      host   = 'localhost:{}'.format(self.PORT),
      url    = '/api/v1/record',
      method = 'POST'
    ))

    now = datetime(2017, 6, 17, 23, 14, 37, tzinfo = timezone.utc)
    for i in range(4):
      with mock.patch('time.time', lambda: (now - timedelta(hours = i)).timestamp()):
        logger.info('Test', extra = {'i': i})

    qs = urlencode({'group': 'hour', 'timezone': 'Europe/Amsterdam'})
    self.getPage('/api/v1/record?' + qs, method = 'HEAD')
    self.assertStatus(200)
    self.assertHeader('X-Record-Count', '1,1,1,1')
    self.assertHeader('X-Record-Group', ','.join([
      '1497729600', '1497733200', '1497736800', '1497740400']))

    qs = urlencode({'group': 'day', 'timezone': 'Europe/Amsterdam'})
    self.getPage('/api/v1/record?' + qs, method = 'HEAD')
    self.assertStatus(200)
    self.assertHeader('X-Record-Count', '2,2')
    self.assertHeader('X-Record-Group', ','.join(['1497650400', '1497736800']))

    qs = urlencode({'group': 'hour', 'timezone': 'Europe/Amsterdam', 'level': logging.ERROR})
    self.getPage('/api/v1/record?' + qs, method = 'HEAD')
    self.assertStatus(200)
    self.assertHeader('X-Record-Count', '')
    self.assertHeader('X-Record-Group', '')

