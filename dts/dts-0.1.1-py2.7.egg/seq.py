from dateutil.parser import parse
from datetime import timedelta

# generator
def _seqGen(first, last, t_delta, t_fmt):
    dt = first
    last_dt = last + t_delta
    while last_dt > dt:
        yield dt.strftime(t_fmt)
        dt = dt + t_delta

# wrapper
def seqGen(first, last, unit, how_long, fmt):
  td = { 'h': (timedelta(hours=how_long), '%Y%m%d-%H'),
       'd': (timedelta(days=how_long),  '%Y%m%d'),
       'w': (timedelta(weeks=how_long), '%Y%m%d') }

  return _seqGen(first, last, td[unit][0], fmt if fmt is not None else td[unit][1])
