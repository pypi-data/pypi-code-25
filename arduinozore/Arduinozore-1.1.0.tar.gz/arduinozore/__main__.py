"""Arduinozore module."""

import argparse
import os
import socket
import sys
from shutil import copyfile
from shutil import get_terminal_size
from shutil import rmtree

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
from arduinozore.handlers.error404handler import My404Handler
from arduinozore.handlers.serialManager import SerialManager
from arduinozore.handlers.ws import WSHandler
from arduinozore.settings import ARDUINO_CODE_FILE_NAME
from arduinozore.settings import ARDUINO_FILE_PATH
from arduinozore.settings import CERT_FOLDER
from arduinozore.settings import CERT_INSTALLER_PATH
from arduinozore.settings import CONFIG_FOLDER
from arduinozore.settings import PORT
from arduinozore.settings import SSL_PORT
from arduinozore.settings import STATIC_INSTALLER_PATH
from arduinozore.settings import STATIC_PATH
from arduinozore.settings import path
from arduinozore.settings import settings
from arduinozore.settings import ssl_opts
from arduinozore.urls import url_pattern
from pyfiglet import Figlet

STATIC_CMD = "chmod +x " + STATIC_INSTALLER_PATH + " && " + STATIC_INSTALLER_PATH
CERT_CMD = "chmod +x " + CERT_INSTALLER_PATH + " && " + CERT_INSTALLER_PATH


def main():
    """Catch main function."""
    p = argparse.ArgumentParser(
        description="Arduinozore server", prog="arduinozore")
    p.add_argument('-hp',
                   '--http_port',
                   type=int,
                   help='Server http port. Default 80')
    p.add_argument('-hsp',
                   '--https_port',
                   type=int,
                   help='Server https port. Default 443. Used for sockets too.')
    p.add_argument('-a',
                   '--arduino',
                   type=str,
                   metavar='path',
                   help='Path where arduino source code will be generated.')
    p.add_argument('--newconfig',
                   action="store_true",
                   help='Delete actual config and make a new one. Warning.')
    args = p.parse_args()

    if args.arduino:
        copy_arduino_code(args.arduino)

    if args.newconfig:
        if os.path.exists(CONFIG_FOLDER):
            rmtree(CONFIG_FOLDER)

    http_port = PORT if args.http_port is None else args.http_port
    ssl_port = SSL_PORT if args.https_port is None else args.https_port

    check_config_folder()

    serial_manager = SerialManager()
    try:
        if not serial_manager.is_alive():
            serial_manager.start()
        index_application = tornado.web.Application(
            url_pattern, default_handler_class=My404Handler, **settings)

        index_application.listen(http_port)
        http_server = tornado.httpserver.HTTPServer(
            index_application,
            ssl_options=ssl_opts
        )
        http_server.listen(ssl_port)
        tornado.ioloop.PeriodicCallback(WSHandler.write_to_clients, 500).start()

        terminal_width = get_terminal_size((80, 20))[0]
        introduction(ssl_port, terminal_width)

        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print('Exiting...'.center(terminal_width))
    except Exception as e:
        print(e)
        sys.exit()
    finally:
        serial_manager.join()


def introduction(ssl_port, terminal_width):
    """Show a message to the user so he knows who we are."""
    app_name = '  Arduinozore'
    TOPBAR = '#' * (terminal_width - 2)

    print('/' + TOPBAR + '\\' + "\n")
    print(Figlet(font='banner').renderText(app_name))
    print('\\' + TOPBAR + '/' + "\n")
    print('/' + TOPBAR + '\\' + "\n")
    HOST = socket.gethostname()
    PORT = ssl_port
    message = 'Listening on: https://{}:{}'.format(HOST, PORT)
    print(message.center(terminal_width))
    sys.stdout.flush()


def check_config_folder():
    """Check if config folder exists, otherwise creates it."""
    try:
        if not os.path.exists(CONFIG_FOLDER):
            print("No configuration folder found, creating one")
            os.makedirs(CONFIG_FOLDER)
            os.makedirs(CERT_FOLDER)
            os.makedirs(STATIC_PATH)
            os.system(STATIC_CMD)
            os.system(CERT_CMD)
            print("Configuration folder created with success.")

    except Exception as e:
        exit(e)


def copy_arduino_code(dest):
    """Copy arduino source code to dest."""
    dst = path(dest, ARDUINO_CODE_FILE_NAME)
    copyfile(ARDUINO_FILE_PATH, dst)
    print("File copied to " + dst)
    exit(0)


if __name__ == "__main__":
    main()
