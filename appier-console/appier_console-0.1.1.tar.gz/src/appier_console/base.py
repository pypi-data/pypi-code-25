#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2018 Hive Solutions Lda.
#
# This file is part of Hive Appier Framework.
#
# Hive Appier Framework is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Appier Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Appier Framework. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2018 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import os
import sys
import time
import json
import threading
import contextlib

import appier

COLOR_RESET = "\033[0m"
COLOR_WHITE = "\033[1;37m"
COLOR_BLACK = "\033[0;30m"
COLOR_BLUE = "\033[0;34m"
COLOR_LIGHT_BLUE = "\033[1;34m"
COLOR_GREEN = "\033[0;32m"
COLOR_LIGHT_GREEN = "\033[1;32m"
COLOR_CYAN = "\033[0;36m"
COLOR_LIGHT_CYAN = "\033[1;36m"
COLOR_RED = "\033[0;31m"
COLOR_LIGHT_RED = "\033[1;31m"
COLOR_PURPLE = "\033[0;35m"
COLOR_LIGHT_PURPLE = "\033[1;35m"
COLOR_BROWN = "\033[0;33m"
COLOR_YELLOW = "\033[1;33m"
COLOR_GRAY = "\033[0;30m"
COLOR_LIGHT_GRAY = "\033[0;37m"

CLEAR_LINE = "\033[K"

COLORS = dict(
    white = COLOR_WHITE,
    black = COLOR_BLACK,
    blue = COLOR_BLUE,
    light_blue = COLOR_LIGHT_BLUE,
    green = COLOR_GREEN,
    light_green = COLOR_LIGHT_GREEN,
    cyan = COLOR_CYAN,
    light_cyan = COLOR_LIGHT_CYAN,
    red = COLOR_RED,
    light_red = COLOR_LIGHT_RED,
    purple = COLOR_PURPLE,
    light_purple = COLOR_LIGHT_PURPLE,
    brown = COLOR_BROWN,
    yellow = COLOR_YELLOW,
    gray = COLOR_GRAY,
    light_gray = COLOR_LIGHT_GRAY
)

class LoaderThread(threading.Thread):
    """
    Thread class to be used to display the loader into
    the output stream in an async fashion.
    """

    _spinners = None

    def __init__(
        self,
        spinner = "point",
        interval = None,
        color = None,
        template = "{{spinner}}",
        stream = sys.stdout,
        *args, **kwargs
    ):
        threading.Thread.__init__(self, *args, **kwargs)
        self.spinner = spinner
        self.interval = interval
        self.color = color
        self.template = template
        self.stream = stream

    def run(self):
        threading.Thread.run(self)

        cls = self.__class__

        color = COLORS.get(self.color, self.color)

        self.running = True

        spinners = cls.spinners()
        spinner = spinners[self.spinner]

        interval = (self.interval or spinner["interval"]) / 1000.0
        frames = spinner["frames"]
        template = appier.legacy.str(self.template)

        index = 0
        is_first = True

        while self.running:
            value = index % len(frames)
            if is_first: is_first = False
            else: self.stream.write(CLEAR_LINE + "\r")
            replacer = frames[value]
            if color: replacer = color + replacer + COLOR_RESET
            label = template.replace("{{spinner}}", replacer)
            self.stream.write(label)
            self.stream.flush()
            time.sleep(interval)
            index += 1

        self.stream.write(CLEAR_LINE + "\r")
        self.stream.flush()

    def stop(self):
        self.running = False

    def set_template(self, value):
        self.template = value

    @classmethod
    def spinners(cls):
        # in case the spinners dictionary is already loaded returns
        # it immediately to the caller method (no reload)
        if cls._spinners: return cls._spinners

        # builds the path to the JSON based spinners file and the
        # loads into memory to be used in the decoding
        spinners_path = os.path.join(
            os.path.dirname(__file__),
            "res", "spinners.json"
        )
        with open(spinners_path, "rb") as file:
            data = file.read()

        # decodes the binary contents as an UTF-8 unicode string
        # ands feeds its value into the JSON loader
        data = data.decode("utf-8")
        cls._spinners = json.loads(data)

        # returns the now "cached" spinners value to the caller
        # method (further calls avoid the loading)
        return cls._spinners

@contextlib.contextmanager
def ctx_loader(*args, **kwargs):
    thread = LoaderThread(*args, **kwargs)
    thread.start()
    try: yield thread
    finally:
        thread.stop()
        thread.join()

def is_tty(stream = sys.stdout):
    """
    Verifies if the provided stream is capable of a TTY like
    interaction (input and output).

    Otherwise its considered to be an output only stream.

    :type stream: Stream
    :param stream: The stream to be tested for TTY like capabilities.
    :rtype: bool
    :return: If the provided stream is TTY capable.
    :see: https://en.wikipedia.org/wiki/Teleprinter
    """

    return hasattr(stream, "isatty") and stream.isatty()

def is_color():
    plat = sys.platform
    supported_platform = not plat == "Pocket PC" and\
        (not plat == "win32" or "ANSICON" in os.environ)
    if not supported_platform or not is_tty(): return False
    return True

if __name__ == "__main__":
    spinners = appier.conf("SPINNERS", None, cast = list)
    timeout = appier.conf("TIMEOUT", 3.0, cast = float)
    color = appier.conf("COLOR", "cyan")
    if not spinners:
        spinners = LoaderThread.spinners()
        spinners = appier.legacy.keys(spinners)
        spinners = sorted(spinners)
    for spinner in spinners:
        with ctx_loader(
            spinner = spinner,
            color = color,
            template = "Spinner '%s' {{spinner}}" % spinner
        ) as loader:
            time.sleep(timeout)
else:
    __path__ = []
