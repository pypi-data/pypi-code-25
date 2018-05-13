from dateutil.parser import parse
from datetime import timedelta, datetime

DT_UNIT = ['h', 'd', 'w']
DTS_DEFAULT_UNIT = 'd'
DTS_DEFAULT_INTERVAL = 1
DTS_DEFAULT_FORMAT = '%Y%m%d'

# generator
def _seqGen(first, last, t_delta, t_fmt):
    dt = first
    last_dt = last + t_delta
    while last_dt > dt:
        yield dt.strftime(t_fmt)
        dt = dt + t_delta
        if dt > last:
          return

# wrapper
def seqGen(first, last, unit='d', how_long=1, fmt='%Y%m%d'):
  if unit not in DT_UNIT:
    raise ValueError("Incorrect unit. It should be 'h', 'd', or 'w'")

  try:
    datetime.strptime(first.strftime(fmt), fmt)
  except ValueError:
    raise ValueError("Incorrect format string.")

  td = { 'h': (timedelta(hours=how_long), '%Y%m%d-%H'),
       'd': (timedelta(days=how_long),  '%Y%m%d'),
       'w': (timedelta(weeks=how_long), '%Y%m%d') }

  return _seqGen(first, last, td[unit][0], fmt if fmt is not None else td[unit][1])
