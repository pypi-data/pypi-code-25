#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Loggly API
# Copyright (c) 2008-2018 Hive Solutions Lda.
#
# This file is part of Hive Loggly API.
#
# Hive Loggly API is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Loggly API is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Loggly API. If not, see <http://www.apache.org/licenses/>.

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

import json
import time

import appier

BASE_URL = "https://logs-01.loggly.com/inputs/"
""" The default base URL for bulk operations to be used
when no other base URL value is provided to the constructor """

BASE_BULK_URL = "https://logs-01.loggly.com/bulk/"
""" The default base URL for bulk operations to be used
when no other base URL value is provided to the constructor """

class API(
    appier.API
):

    def __init__(self, *args, **kwargs):
        appier.API.__init__(self, *args, **kwargs)
        self.token = appier.conf("LOGGLY_TOKEN", None)
        self.buffer_size = appier.conf("LOGGLY_BUFFER_SIZE", 128)
        self.timeout = appier.conf("LOGGLY_TIMEOUT", 30)
        self.base_url = kwargs.get("base_url", BASE_URL)
        self.base_bulk_url = kwargs.get("base_bulk_url", BASE_BULK_URL)
        self.token = kwargs.get("token", self.token)
        self.buffer_size = kwargs.get("buffer_size", self.buffer_size)
        self.timeout = kwargs.get("timeout", self.timeout)
        self.delayer = kwargs.get("delayer", None)
        self._build_url()
        self._last_flush = time.time()
        self._buffer = []

    def log(self, payload, tag = "default", silent = True):
        url = self.token_url + "tags/%s" % tag
        contents = self.post(url, data_j = payload, silent = silent)
        return contents

    def log_bulk(self, logs, tag = "default", silent = True):
        url = self.token_bulk_url + "tags/%s" % tag
        buffer = []
        for log in logs:
            log_s = json.dumps(log)
            log_s = appier.legacy.bytes(log_s, encoding = "utf-8")
            buffer.append(log_s)
        data = b"\n".join(buffer)
        contents = self.post(url, data = data, silent = silent)
        return contents

    def log_buffer(self, payload):
        self._buffer.append(payload)
        should_flush = len(self._buffer) >= self.buffer_size or\
            time.time() > self._last_flush + self.timeout
        if should_flush: self._flush_buffer()

    def _flush_buffer(self, force = False):
        # retrieves some references from the current instance that
        # are going to be used in the flush operation
        buffer = self._buffer

        # verifies if the buffer is empty and if that's the case and
        # the force flag is not set, returns immediately
        if not buffer and not force: return

        # creates the lambda function that is going to be used for the
        # bulk flushing operation of the buffer, this is going to be
        # called on a delayed (async fashion) so that no blocking occurs
        # in the current logical flow
        call_log = lambda: self.log_bulk(buffer, tag = "default")

        # schedules the call log operation and then empties the buffer
        # so that it's no longer going to be used (flushed), notice that
        # in case there's no delayer available calls the method immediately
        if self.delayer: self.delayer(call_log)
        else: call_log()
        self._buffer = []
        self._last_flush = time.time()

    def _build_url(self):
        self.token_url = "%s%s/" % (self.base_url, self.token)
        self.token_bulk_url = "%s%s/" % (self.base_bulk_url, self.token)
