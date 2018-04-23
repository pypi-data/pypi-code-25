# coding: utf-8

import sys
import argparse
from .server.app import run_app
from .common import DEFAULT_HTTP_PORT


def main():
    print("sys.argv: %s" % sys.argv)
    print("sys.path: %s" % sys.path)

    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('-h', '--host', default="")
    parser.add_argument('-p', '--port', type="int", default=DEFAULT_HTTP_PORT)
    parser.add_argument('-c', '--config')
    args = parser.parse_args()

    run_app(args.port, args.host, args.config)


main()
