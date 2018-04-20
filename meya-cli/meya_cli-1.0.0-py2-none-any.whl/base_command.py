# Copyright 2018 Locl Interactive Inc. (d/b/a Meya.ai). All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
from __future__ import absolute_import

import argparse

import os


class BaseCommand(object):
    INVOCATION = None
    DESCRIPTION = ""
    ARGUMENTS = []

    def __init__(self, config, argv):
        self.config = config
        self.args = type(self).arg_parser().parse_args(argv)

    @property
    def api(self):
        from meya_cli.meya_api import MeyaAPI
        return MeyaAPI(self.config.api_key, base_url=self.config.api_root)

    @classmethod
    def arg_parser(cls):
        parser = argparse.ArgumentParser(prog="meya-cli " + cls.INVOCATION,
                                         description=cls.DESCRIPTION,
                                         add_help=False)
        for name, arg_spec in cls.ARGUMENTS:
            parser.add_argument(name, **arg_spec)
        return parser

    def perform(self):
        pass

    @property
    def file_api_root(self):
        return "files/" + self.config.bot_id + "/"
