import sys
import argparse
from argparse import RawTextHelpFormatter
from dateutil.parser import parse
import pkg_resources  # part of setuptools

from dts.seq import seqGen, DT_UNIT, DTS_DEFAULT_UNIT, DTS_DEFAULT_INTERVAL, DTS_DEFAULT_FORMAT

version = pkg_resources.require("dts")[0].version

description = """
dts is a seq util for datetimes

- Version: {version}
- Github: https://github.com/KwangYeol/dts

- Examples:

  $ dts 20180501 20180503
  20180501
  20180502
  20180503

  $ dts 20180501-0900 20180501-1200 -i h1 -f '%Y-%m-%dT%H:%M:%S'
  2018-05-01T09:00:00
  2018-05-01T10:00:00
  2018-05-01T11:00:00
  2018-05-01T12:00:00


""".format(version=version)

def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    # Do argument parsing here (eg. with argparse) and anything else
    # you want your project to do.
    parser = argparse.ArgumentParser(description=description, formatter_class=RawTextHelpFormatter)
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

    fmt = DTS_DEFAULT_FORMAT
    if args.format:
      fmt = args.format

    unit = DTS_DEFAULT_UNIT
    how_long = DTS_DEFAULT_INTERVAL

    if args.interval and len(args.interval) >= 2 and args.interval[0] in DT_UNIT:
      unit = args.interval[0]
      how_long = int(args.interval[1:])

    try:
      hseq = seqGen(first, last, unit, how_long, fmt)
    except ValueError as ex:
      print(ex)
      return

    for d in hseq:
      print(d)

if __name__ == "__main__":
    main()