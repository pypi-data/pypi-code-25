#!/usr/bin/env python3

import os
import sys
import argparse
import logging
import yaml
from .config import load_config
from .mqtt2mqtt import Mqtt2Mqtt

__version__ = '0.1.0'
LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s'


def main():
    argp = argparse.ArgumentParser(description='MQTT to MQTT')
    argp.add_argument('-c', '--config', help='path to configuration file (YAML format)', required=True)
    argp.add_argument('-D', '--debug', help='print debug messages', action='store_true')
    argp.add_argument('-t', '--test', help='test parse config', action='store_true')
    argp.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    args = argp.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO, format=LOG_FORMAT)

    try:
        config = load_config(args.config)

        if args.test:
            return

        Mqtt2Mqtt(config)

    except KeyboardInterrupt as e:
        return
    except Exception as e:
        logging.error(e)
        if os.getenv('DEBUG', False):
            raise e
        sys.exit(1)


if __name__ == '__main__':
    main()
