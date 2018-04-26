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
import six
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class Base64(CloudFormationLintRule):
    """Check if Base64 values are correct"""
    id = 'E1021'
    shortdesc = 'Base64 validation of parameters'
    description = 'Making sure the function not is of list'
    tags = ['base', 'functions', 'base64']

    def match(self, cfn):
        """Check CloudFormation Base64"""

        matches = list()

        base64_objs = cfn.search_deep_keys('Fn::Base64')
        for base64_obj in base64_objs:
            tree = base64_obj[:-1]
            value_obj = base64_obj[-1]
            if isinstance(value_obj, dict):
                if len(value_obj) == 1:
                    for key, _ in value_obj.items():
                        if key == 'Fn::Split':
                            message = "Base64 needs a string at {0}"
                            matches.append(RuleMatch(
                                tree[:], message.format('/'.join(map(str, tree)))))
                else:
                    message = "Base64 needs a string not a map or list at {0}"
                    matches.append(RuleMatch(
                        tree[:], message.format('/'.join(map(str, tree)))))
            elif not isinstance(value_obj, six.string_types):
                message = "Base64 needs a string at {0}"
                matches.append(RuleMatch(
                    tree[:], message.format('/'.join(map(str, tree)))))

        return matches
