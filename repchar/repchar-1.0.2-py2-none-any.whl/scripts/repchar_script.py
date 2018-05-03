# -*- coding: UTF-8 -*-

"""
repchar script
"""

from io import open
import argparse
import logging

from repchar import CharReporter
from repchar import __version__

def main():
    p = argparse.ArgumentParser()
    p.add_argument("infilename",
            metavar="INFILENAME",
            help=u"Filename")
    p.add_argument("-o", "--outfile", "--out",
            metavar="OUTFILENAME",
            help=u"Filename for report",
            required=True,
            dest="outfilename")
    p.add_argument("-v", "--verbose",
            help=u"Set log level to INFO.",
            default=False,
            action="store_true",
            dest="b_verbose")
    p.add_argument("--version",
            action="version",
            version="%(prog)s {version}".format(version=__version__))
    p.add_argument("-c", "--comb", "--combining",
            help=u"Create special report for "\
                    u"combining characters",
            default=False,
            action="store_true",
            dest="b_combining")
    args = p.parse_args()
    if args.b_verbose:
        logging.basicConfig(level=logging.INFO)
    r = CharReporter(combining=args.b_combining)
    with open(args.infilename, "rb") as infile:
        cnt = 0
        for line in infile:
            line = line.strip()
            cnt += 1
            line = line.decode("UTF-8")
            r.feed(line)
    report = r.report()
    with open(args.outfilename, "w", encoding="UTF-8") as reportfile:
        reportfile.write(report)

if __name__ == "__main__":
    main()
