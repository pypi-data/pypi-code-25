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


class Split(CloudFormationLintRule):
    """Check if Split values are correct"""
    id = 'E1018'
    shortdesc = 'Split validation of parameters'
    description = 'Making sure the split function is properly configured'
    tags = ['base', 'functions', 'split']

    def match(self, cfn):
        """Check CloudFormation Join"""

        matches = list()

        split_objs = cfn.search_deep_keys('Fn::Split')

        supported_functions = [
            'Fn::Base64',
            'Fn::FindInMap',
            'Fn::GetAtt',
            'Fn::GetAZs',
            'Fn::ImportValue',
            'Fn::If',
            'Fn::Join',
            'Fn::Select',
            'Ref'
        ]

        for split_obj in split_objs:
            split_value_obj = split_obj[-1]
            tree = split_obj[:-1]
            if isinstance(split_value_obj, list):
                if len(split_value_obj) == 2:
                    split_delimiter = split_value_obj[0]
                    split_string = split_value_obj[1]
                    if not isinstance(split_delimiter, six.string_types):
                        message = "Split delimiter has to be of type string for {0}"
                        matches.append(RuleMatch(
                            tree + [0], message.format('/'.join(map(str, tree)))))
                    if isinstance(split_string, dict):
                        if len(split_string) == 1:
                            for key, _ in split_string.items():
                                if key not in supported_functions:
                                    message = "Split unsupported function for {0}"
                                    matches.append(RuleMatch(
                                        tree + [key], message.format('/'.join(map(str, tree)))))
                        else:
                            message = "Split list of singular function or string for {0}"
                            matches.append(RuleMatch(
                                tree, message.format('/'.join(map(str, tree)))))
                    elif not isinstance(split_string, six.string_types):
                        message = "Split has to be of type string or valid function for {0}"
                        matches.append(RuleMatch(
                            tree, message.format('/'.join(map(str, tree)))))
                else:
                    message = "Split should be an array of 2 for {0}"
                    matches.append(RuleMatch(
                        tree, message.format('/'.join(map(str, tree)))))
            else:
                message = "Split should be an array of 2 for {0}"
                matches.append(RuleMatch(
                    tree, message.format('/'.join(map(str, tree)))))
        return matches
