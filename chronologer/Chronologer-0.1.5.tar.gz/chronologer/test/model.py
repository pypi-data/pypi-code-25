import time
import queue
import unittest
import logging.handlers
from urllib.parse import urlencode, parse_qsl

from . import setUpModule  # @UnusedImport
from ..model import createRecord


class TestExceptionData(unittest.TestCase):

  record = None
  '''Logging record under test'''


  def setUp(self):
    with self.assertLogs('', logging.ERROR) as ctx:
      try:
        1 / 0
      except ZeroDivisionError:
        logging.exception('Thou hast ill math')
    self.record = ctx.records[0]

  def testExceptionHttpHandlerDirectly(self):
    # see ``HTTPHandler.mapLogRecord`` and ``HTTPHandler.emit``
    postData = urlencode(self.record.__dict__)
    actual = createRecord(**dict(parse_qsl(postData)))

    self.assertEqual('root', actual.name)
    self.assertEqual(logging.ERROR, actual.level)
    self.assertEqual('Thou hast ill math', actual.message)
    self.assertAlmostEqual(time.time(), actual.ts, delta = 1)

    self.assertTrue(actual.logrec['error']['exc_info'].startswith(
      "(<class 'ZeroDivisionError'>, ZeroDivisionError('division by zero',), <traceback object"))
    self.assertTrue(actual.logrec['error']['exc_text'].startswith(
      'Traceback (most recent call last):'))
    self.assertTrue(actual.logrec['error']['exc_text'].endswith(
      'ZeroDivisionError: division by zero'))

  def testExceptionViaQueueHandler(self):
    q = queue.Queue()
    h = logging.handlers.QueueHandler(q)
    h.emit(self.record)
    record = q.get_nowait()

    # see ``HTTPHandler.mapLogRecord`` and ``HTTPHandler.emit``
    postData = urlencode(record.__dict__)
    actual = createRecord(**dict(parse_qsl(postData)))

    self.assertEqual('root', actual.name)
    self.assertEqual(logging.ERROR, actual.level)
    self.assertEqual('Thou hast ill math', actual.message)
    self.assertAlmostEqual(time.time(), actual.ts, delta = 1)

    self.assertTrue(actual.logrec['error']['exc_info'] is None, 'Stripped by QueueHandler')
    self.assertTrue(actual.logrec['error']['exc_text'].startswith(
      'Traceback (most recent call last):'))
    self.assertTrue(actual.logrec['error']['exc_text'].endswith(
      'ZeroDivisionError: division by zero'))

