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


class InterfaceConfiguration(CloudFormationLintRule):
    """Check if Metadata Interface Configuration are configured correctly"""
    id = 'E4001'
    shortdesc = 'Metadata Interface have appropriate properties'
    description = 'Metadata Interface properties are properly configured'
    tags = ['base', 'metadata']

    valid_keys = [
        'ParameterGroups',
        'ParameterLabels'
    ]

    def match(self, cfn):
        """Check CloudFormation Metadata Interface Configuration"""

        matches = list()

        strinterface = 'AWS::CloudFormation::Interface'

        metadata_obj = cfn.template.get('Metadata', {})
        if metadata_obj:
            interfaces = metadata_obj.get(strinterface, {})
            if isinstance(interfaces, dict):
                for interface in interfaces:
                    if interface not in self.valid_keys:
                        message = "Metadata Interface has invalid property {0}"
                        matches.append(RuleMatch(
                            ['Metadata', strinterface, interface],
                            message.format(interface)
                        ))
                parameter_groups = interfaces.get('ParameterGroups', [])
                for index, value in enumerate(parameter_groups):
                    for key in value:
                        if key not in ['Label', 'Parameters']:
                            message = "Metadata Interface has invalid property {0}"
                            matches.append(RuleMatch(
                                ['Metadata', strinterface, 'ParameterGroups', index, key],
                                message.format(key)
                            ))

        return matches
