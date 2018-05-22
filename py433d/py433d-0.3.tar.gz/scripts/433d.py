#!/usr/bin/env python3

import logging
from argparse import ArgumentParser
from logging.handlers import RotatingFileHandler
from queue import Queue
from signal import (
    signal,
    SIGINT
)
from threading import Thread

from py433 import (
    tcp_server,
    transmitter,
    receiver,
    mqtt,
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

def setup_logging(conf):
    rootLogger = logging.getLogger()
    rootLogger.handlers = []
    rootLogger.setLevel(conf.log_level)

    logFormatter = logging.Formatter("%(asctime)-15s - [%(levelname)s] %(module)s: %(message)s")

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    fileHandler = logging.handlers.RotatingFileHandler(args.log or conf.log_filename, maxBytes=(1024 * 1024),
                                                       backupCount=7)
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

def stop_all():
    rx.stop()
    tx.stop()
    srv.stop()
    conf.stop()

running = True

def exithandler(self, signal):
    running = False
    stop_all()
    logging.info("Server stopped")

signal(SIGINT, exithandler)

while running:
    conf = configuration.load(filename=args.conf)
    conf.watch(stop_all)

    setup_logging(conf)

    logging.info("Server started")

    q = Queue()

    tx = transmitter(q, messages=conf.messages, pin=conf.tx_pin, protocol=conf.tx_protocol, pulse=conf.tx_pulse)
    t1 = Thread(target=tx.run)
    t1.daemon = True
    t1.start()

    srv = tcp_server(port=args.port or conf.port, handler=lambda m: q.put(m))
    t2 = Thread(target=srv.run)
    t2.daemon = True
    t2.start()

    m = None
    rx_handler = lambda x: print(x)
    if conf.mqtt_host:
        m = mqtt(host=conf.mqtt_host,
                 port=conf.mqtt_port,
                 username=conf.mqtt_username,
                 password=conf.mqtt_password,
                 codes=conf.codes)
        rx_handler = lambda x: m.post(x)

    rx = receiver(pin=conf.rx_pin, handler=rx_handler)
    t3 = Thread(target=rx.run)
    t3.daemon = True
    t3.start()

    t1.join()
    t2.join()
    t3.join()
