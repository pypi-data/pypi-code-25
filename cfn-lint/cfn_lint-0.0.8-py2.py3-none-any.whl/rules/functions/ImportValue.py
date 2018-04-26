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


class ImportValue(CloudFormationLintRule):
    """Check if ImportValue values are correct"""
    id = 'E1016'
    shortdesc = 'ImportValue validation of parameters'
    description = 'Making sure the function not is of list'
    tags = ['base', 'functions', 'importvalue']

    def match(self, cfn):
        """Check CloudFormation ImportValue"""

        matches = list()

        iv_objs = cfn.search_deep_keys('Fn::ImportValue')

        supported_functions = [
            'Fn::Base64',
            'Fn::FindInMap',
            'Fn::If',
            'Fn::Join',
            'Fn::Select',
            'Fn::Split',
            'Fn::Sub',
            'Ref'
        ]

        for iv_obj in iv_objs:
            iv_value = iv_obj[-1]
            tree = iv_obj[:-1]
            if isinstance(iv_value, dict):
                if len(iv_value) == 1:
                    for key, _ in iv_value.items():
                        if key not in supported_functions:
                            message = "ImportValue should be using supported function for {0}"
                            matches.append(RuleMatch(
                                tree, message.format('/'.join(map(str, tree[:-1])))))
                else:
                    message = "ImportValue should have one mapping for {0}"
                    matches.append(RuleMatch(
                        tree, message.format('/'.join(map(str, tree[:-1])))))
            elif not isinstance(iv_value, six.string_types):
                message = "ImportValue should have supported function or string for {0}"
                matches.append(RuleMatch(
                    tree, message.format('/'.join(map(str, tree)))))
        return matches
