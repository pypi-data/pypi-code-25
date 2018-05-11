import sys
import argparse
from dateutil.parser import parse

from dts.seq import seqGen

def main():
  parser = argparse.ArgumentParser(description='seq for datetime')
  parser.add_argument('FIRST', metavar='FIRST',
          help='first date of the seq. For example, 2018-05-01, 20180501, 20180501-0900, 2018-05-01T09:00')
  parser.add_argument('LAST', metavar='LAST',
          help='last date of the seq. See also, FIRST')
  parser.add_argument('-i', '--interval', help='interval: h1, d1, w1. default value is d1')
  parser.add_argument('-f', '--format', help='see also, datetime.strftime')

  args = parser.parse_args()

  try:
    first = parse(args.FIRST)
    last = parse(args.LAST)
  except:
    print("invalid datetime format")
    sys.exit(1)

  fmt = None
  if args.format:
    fmt = args.format

  unit = 'd'
  how_long = 1

  if args.interval and len(args.interval) >= 2 and args.interval[0] in ['h', 'd', 'w']:
    unit = args.interval[0]
    how_long = int(args.interval[1:])

  hseq = seqGen(first, last, unit, how_long, fmt)

  for d in hseq:
    if parse(d) > last:
        continue
    print(d)
