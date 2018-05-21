import ast
import logging
import itertools
from collections import namedtuple

import pytz


__all__ = 'createRecord', 'groupTimeseries'


RefRec = logging.makeLogRecord({})
Record = namedtuple('Record', ('name', 'ts', 'level', 'message', 'logrec'))


def createRecord(**kwargs):
    '''Create a logging record.
    See https://docs.python.org/3/library/logging.html#logrecord-attributes'''

    for k, v in kwargs.items():
      try:
        kwargs[k] = ast.literal_eval(v)
      except (SyntaxError, ValueError):
        pass

    name  = kwargs.pop('name')
    ts    = kwargs.pop('created')
    level = kwargs.pop('levelno')

    # There's no message but only 'msg' when no string interpolation takes place
    message = kwargs.pop('message') if 'message' in kwargs else kwargs['msg']

    # Remove redundant attributes. 'asctime' is not always present.
    for k in ('levelname', 'asctime'):
      kwargs.pop(k, None)

    error = {}
    if not kwargs['exc_text']:
      del kwargs['exc_info'], kwargs['exc_text']
    else:
      error.update(exc_info = kwargs.pop('exc_info'), exc_text = kwargs.pop('exc_text'))

    meta = {}
    data = {}
    for k, v in kwargs.items():
      if hasattr(RefRec, k):
        meta[k] = v
      else:
        data[k] = v

    scope  = locals()
    logrec = {n: scope[n] for n in ('data', 'meta', 'error') if scope[n]}

    return Record(name, ts, level, message, logrec)


intervals = {
  'day'  : {'hour': 0, 'minute': 0, 'second': 0},
  'hour' : {'minute': 0, 'second': 0}
}

def groupTimeseries(seq, interval, tz):
  '''Group tuple(dt, count) sequence in coarser time interval'''

  sub = intervals[interval]
  tz  = pytz.timezone(tz)
  for k, g in itertools.groupby(seq, key = lambda v: v[0].astimezone(tz).replace(**sub)):
    yield k, sum(v[1] for v in g)

