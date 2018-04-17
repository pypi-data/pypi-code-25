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
    """Check if Outputs are configured correctly"""
    id = 'E6001'
    shortdesc = 'Outputs have appropriate properties'
    description = 'Making sure the outputs are properly configured'
    tags = ['base', 'outputs']

    valid_keys = [
        'Value',
        'Export',
        'Description',
        'Condition'
    ]

    def match(self, cfn):
        """Check CloudFormation Outputs"""

        matches = list()

        outputs = cfn.template.get('Outputs', {})
        if outputs:
            for output_name, output_value in outputs.items():
                for prop in output_value:
                    if prop not in self.valid_keys:
                        message = "Output {0} has invalid property {1}"
                        matches.append(RuleMatch(
                            ['Outputs', output_name, prop],
                            message.format(output_name, prop)
                        ))

        return matches
