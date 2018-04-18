#!/usr/bin/env python
# coding: utf-8

import sys
import traceback

from .cli import parser
from .core import program


def main(argv=sys.argv):

    args = parser.parse_args()

    try:
        return_code = program(args)
        sys.exit(return_code)

    except Exception as e:
        error_name = type(e).__name__
        stacktrace = traceback.format_exc()

        if args.dev:
            print stacktrace.strip()

        else:
            sys.stderr.write("{0}: {1}\n".format(error_name, e.message))


if __name__ == '__main__':

    main()
