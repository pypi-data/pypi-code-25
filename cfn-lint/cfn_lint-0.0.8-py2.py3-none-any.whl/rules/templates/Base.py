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


class Base(CloudFormationLintRule):
    """Check Base Template Settings"""
    id = 'E1001'
    shortdesc = 'Basic CloudFormation Template Configuration'
    description = 'Making sure the basic CloudFormation template componets ' + \
                  'are propery configured'
    tags = ['base']

    valid_keys = [
        'AWSTemplateFormatVersion',
        'Resources',
        'Description',
        'Metadata',
        'Parameters',
        'Outputs',
        'Mappings',
        'Conditions',
        'Rules',
        'Transform'
    ]

    required_keys = [
        'AWSTemplateFormatVersion',
        'Resources'
    ]

    def match(self, cfn):
        """Basic Matching"""
        matches = list()

        top_level = []
        for x in cfn.template:
            top_level.append(x)
            if x not in self.valid_keys:
                message = "Top level item {0} isn't valid"
                matches.append(RuleMatch(
                    [x],
                    message.format(x)
                ))

        for y in self.required_keys:
            if y not in top_level:
                message = "Missing top level item {0} to file module"
                matches.append(RuleMatch(
                    ['AWSTemplateFormatVersion'],
                    message.format(y)
                ))

        return matches
