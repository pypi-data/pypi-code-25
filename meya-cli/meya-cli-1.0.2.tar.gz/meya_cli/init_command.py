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

import os

from meya_cli import MeyaConfig, DownloadCommand
from meya_cli.base_command import BaseCommand


class InitCommand(BaseCommand):
    INVOCATION = "init"
    DESCRIPTION = "initialize a Meya bot, if you know your user api key & " \
                  "bot ID. The easiest way to use this command is to " \
                  "copy it from bot studio."
    ARGUMENTS = [
        ("api_key", {"help": "api key, found in bot studio."}),
        ("bot_id", {"help": "id of bot, found in bot studio."}),
        ("api_root", {"help": "optional, specify a different URL "
                              "with which to access the Meya API.",
                      "nargs": "?"})
    ]

    def perform(self):
        with open(os.path.join('meya-config.yaml'),
                  'w') as f:
            f.write("api_key: " + self.args.api_key + "\n")
            f.write("bot_id: " + self.args.bot_id + "\n")

            # api_root may or may not be provided
            # generally in production settings, api_root is not specified
            # therefore MeyaConfig will specify the default value
            # TODO: write unit test for this
            kwargs = {}
            if self.args.api_root:
                f.write("api_root: " + self.args.api_root + "\n")
                kwargs["api_root"] = self.args.api_root

        new_config = MeyaConfig(".", self.args.api_key,
                                self.args.bot_id, **kwargs)
        DownloadCommand(new_config, []).perform()
