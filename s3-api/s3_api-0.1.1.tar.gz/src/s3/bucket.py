#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Amazon S3 API
# Copyright (c) 2008-2018 Hive Solutions Lda.
#
# This file is part of Hive Amazon S3 API.
#
# Hive Amazon S3 API is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Amazon S3 API is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Amazon S3 API. If not, see <http://www.apache.org/licenses/>.

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

class BucketAPI(object):

    def list_buckets(
        self,
        prefix = None,
        marker = None,
        max_keys = None
    ):
        url = self.base_url
        contents = self.get(
            url,
            params = {
                "prefix": prefix,
                "marker": marker,
                "max-keys": max_keys
            },
            sign = True
        )
        return contents
