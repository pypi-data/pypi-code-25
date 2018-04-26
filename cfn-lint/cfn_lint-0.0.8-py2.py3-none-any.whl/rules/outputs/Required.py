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


class Required(CloudFormationLintRule):
    """Check if Outputs have required properties"""
    id = 'E6002'
    shortdesc = 'Outputs have required properties'
    description = 'Making sure the outputs have required properties'
    tags = ['base', 'outputs']

    def match(self, cfn):
        """Check CloudFormation Outputs"""

        matches = list()

        outputs = cfn.template.get('Outputs', {})
        if outputs:
            for output_name, output_value in outputs.items():
                if 'Value' not in output_value:
                    message = "Output {0} is missing property {1}"
                    matches.append(RuleMatch(
                        ['Outputs', output_name, 'Value'],
                        message.format(output_name, 'Value')
                    ))
                if 'Export' in output_value:
                    if 'Name' not in output_value['Export']:
                        message = "Output {0} is missing property {1}"
                        matches.append(RuleMatch(
                            ['Outputs', output_name, 'Export'],
                            message.format(output_name, 'Name')
                        ))

        return matches
