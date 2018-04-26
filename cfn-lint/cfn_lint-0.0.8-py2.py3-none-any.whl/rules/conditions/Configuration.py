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
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class Configuration(CloudFormationLintRule):
    """Check if Conditions are configured correctly"""
    id = 'E8001'
    shortdesc = 'Conditions have appropriate properties'
    description = 'Check if Conditions are properly configured'
    tags = ['base', 'conditions']

    condition_keys = [
        'Fn::And',
        'Fn::Equals',
        'Fn::If',
        'Fn::Not',
        'Fn::Or'
    ]

    def match(self, cfn):
        """Check CloudFormation Conditions"""

        matches = list()

        conditions = cfn.template.get('Conditions', {})
        if conditions:
            for condname, condobj in conditions.items():
                if not isinstance(condobj, dict):
                    message = "Condition {0} has invalid property"
                    matches.append(RuleMatch(
                        ['Conditions', condname],
                        message.format(condname)
                    ))
                else:
                    if len(condobj) != 1:
                        message = "Condition {0} has to many intrinsic conditions"
                        matches.append(RuleMatch(
                            ['Conditions', condname],
                            message.format(condname)
                        ))

        return matches
