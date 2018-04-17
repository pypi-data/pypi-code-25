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


class Select(CloudFormationLintRule):
    """Check if Select values are correct"""
    id = 'E1017'
    shortdesc = 'Select validation of parameters'
    description = 'Making sure the function not is of list'
    tags = ['base', 'functions', 'select']

    def match(self, cfn):
        """Check CloudFormation Select"""

        matches = list()

        select_objs = cfn.search_deep_keys('Fn::Select')

        supported_functions = [
            'Fn::FindInMap',
            'Fn::GetAtt',
            'Fn::GetAZs',
            'Fn::If',
            'Fn::Split',
            'Fn::Cidr',
            'Ref'
        ]

        for select_obj in select_objs:
            select_value_obj = select_obj[-1]
            tree = select_obj[:-1]
            if isinstance(select_value_obj, list):
                if len(select_value_obj) == 2:
                    index_obj = select_value_obj[0]
                    list_of_objs = select_value_obj[1]
                    if isinstance(index_obj, dict):
                        if len(index_obj) == 1:
                            for index_key, _ in index_obj:
                                if index_key not in ['Ref', 'Fn::FindInMap']:
                                    message = "Select index should be int, Ref, FindInMap for {0}"
                                    matches.append(RuleMatch(
                                        tree, message.format('/'.join(map(str, tree)))))
                    elif not isinstance(index_obj, six.integer_types):
                        message = "Select index should be int, Ref, FindInMap for {0}"
                        matches.append(RuleMatch(
                            tree, message.format('/'.join(map(str, tree)))))
                    if isinstance(list_of_objs, dict):
                        if len(list_of_objs) == 1:
                            for key, _ in list_of_objs.items():
                                if key not in supported_functions:
                                    message = "Key {0} should be a list for {1}"
                                    matches.append(RuleMatch(
                                        tree, message.format(key, '/'.join(map(str, tree)))))
                        else:
                            message = "Select should be a list of 2 elements for {0}"
                            matches.append(RuleMatch(
                                tree, message.format('/'.join(map(str, tree)))))
                    else:
                        message = "Select should be an array of values for {0}"
                        matches.append(RuleMatch(
                            tree, message.format('/'.join(map(str, tree)))))
                else:
                    message = "Select should be a list of 2 elements for {0}"
                    matches.append(RuleMatch(
                        tree, message.format('/'.join(map(str, tree)))))
            else:
                message = "Select should be a list of 2 elements for {0}"
                matches.append(RuleMatch(
                    tree, message.format('/'.join(map(str, tree)))))
        return matches
