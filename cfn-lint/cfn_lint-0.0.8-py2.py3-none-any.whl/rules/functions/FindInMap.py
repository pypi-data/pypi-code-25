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


class FindInMap(CloudFormationLintRule):
    """Check if FindInMap values are correct"""
    id = 'E1011'
    shortdesc = 'FindInMap validation of configuration'
    description = 'Making sure the function is a list of appropriate config'
    tags = ['base', 'functions', 'getatt']

    def check_ref(self, obj, tree):
        """
            Check that obj is a dict with Ref as the only key
            Mappings only support Ref inside them
        """
        matches = list()
        if isinstance(obj, dict):
            if len(obj) == 1:
                for key_name, _ in obj.items():
                    if key_name not in ['Ref', 'Fn::FindInMap']:
                        message = "FindInMap only supports Ref and Fn::FindInMap for {0}"
                        matches.append(RuleMatch(
                            tree[:] + [key_name], message.format('/'.join(map(str, tree)))))

        return matches

    def match(self, cfn):
        """Check CloudFormation GetAtt"""

        matches = list()

        findinmaps = cfn.search_deep_keys('Fn::FindInMap')
        mappings = cfn.get_mappings()
        for findinmap in findinmaps:
            tree = findinmap[:-1]
            map_obj = findinmap[-1]
            if not isinstance(map_obj, list):
                message = "FindInMap is a list with 3 values for {0}"
                matches.append(RuleMatch(
                    tree[:], message.format('/'.join(tree))))
                continue
            if len(map_obj) == 3:
                map_name = map_obj[0]
                first_key = map_obj[1]
                second_key = map_obj[2]
                if not isinstance(map_name, six.string_types):
                    message = "Map Name should be a string for {0}"
                    matches.append(RuleMatch(
                        tree[:] + [0], message.format('/'.join(map(str, tree)))))
                else:
                    if map_name not in mappings:
                        message = "Map Name {0} doesnt exist for {0}"
                        matches.append(RuleMatch(
                            tree[:] + [0], message.format(map_name, '/'.join(map(str, tree)))))

                if isinstance(first_key, (six.string_types, dict, int)):
                    if isinstance(first_key, dict):
                        matches.extend(self.check_ref(first_key, tree[:] + [1]))
                else:
                    message = "Map Name should be a string, int, FindInMap, or Ref for {0}"
                    matches.append(RuleMatch(
                        tree[:] + [1], message.format('/'.join(map(str, tree)))))

                if isinstance(second_key, (six.string_types, dict, int)):
                    if isinstance(second_key, dict):
                        matches.extend(self.check_ref(second_key, tree[:] + [2]))
                else:
                    message = "Map Name should be a string, int, FindInMap, or Ref for {0}"
                    matches.append(RuleMatch(
                        tree[:] + [2], message.format('/'.join(tree))))

            else:
                message = "FindInMap is a list with 3 values for {0}"
                matches.append(RuleMatch(
                    tree[:] + [1], message.format('/'.join(map(str, tree)))))

        return matches
