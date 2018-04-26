"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Licensed under the Apache License, Version 2.0 (the "License").
  You may not use this file except in compliance with the License.
  A copy of the License is located at

      http://www.apache.org/licenses/LICENSE-2.0

  or in the "license" file accompanying this file. This file is distributed
  on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
  express or implied. See the License for the specific language governing
  permissions and limitations under the License.
"""


class Formatter(object):
    """Generic Formatter"""
    def format(self, match):
        """Format output"""
        formatstr = u"{0} {1}\n{2}:{3}:{4}\n"
        return formatstr.format(
            match.rule.id,
            match.message,
            match.filename,
            match.linenumber,
            match.columnnumber
        )


class QuietFormatter(object):
    """Quiet Formatter"""
    def format(self, match):
        """Format output"""
        formatstr = u"{0} {1}:{2}"
        return formatstr.format(
            match.rule,
            match.filename,
            match.linenumber
        )


class ParseableFormatter(object):
    """Parseable Formmatter"""
    def format(self, match):
        """Format output"""
        formatstr = u"{0}:{1}:{2}:{3}:{4}: [{5}] {6}"
        return formatstr.format(
            match.filename,
            match.linenumber,
            match.columnnumber,
            match.linenumberend,
            match.columnnumberend,
            match.rule.id,
            match.message
        )
