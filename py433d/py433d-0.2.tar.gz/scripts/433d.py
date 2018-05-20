#!/usr/bin/env python3

import logging
from argparse import ArgumentParser
from logging.handlers import RotatingFileHandler
from queue import Queue
from threading import Thread

from py433 import (
    server,
    transmitter,
    configuration,
    __version__,
    defaults
)

parser = ArgumentParser(description='Server for 433Mhz communication')
parser.add_argument('-v', '--version', help="Show version")
parser.add_argument('-c', '--conf', default=defaults.config, help="Configuration file")
parser.add_argument('-p', '--port', help="Set port to listen on")
parser.add_argument('-l', '--log', help="Log file")
args = parser.parse_args()

if args.version:
    print(__version__)
    exit(0)

conf = configuration.load(filename=args.conf)

rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)

logFormatter = logging.Formatter("%(asctime)-15s - [%(levelname)s] %(module)s: %(message)s")

rootLogger.handlers[0].setFormatter(logFormatter)

# consoleHandler = logging.StreamHandler()
# consoleHandler.setFormatter(logFormatter)
# rootLogger.addHandler(consoleHandler)

fileHandler = logging.handlers.RotatingFileHandler(args.log or conf.log_filename, maxBytes=(1024 * 1024), backupCount=7)
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

q = Queue()

tx = transmitter(q, messages=conf.messages, pin=conf.tx_pin, protocol=conf.tx_protocol, pulse=conf.tx_pulse)
t1 = Thread(target=tx.run)
t1.daemon = True
t1.start()

srv = server(port=args.port or conf.port, handler=lambda m: q.put(m))
t2 = Thread(target=srv.start)
t2.daemon = True
t2.start()

t1.join()
t2.join()