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


class InterfaceParameterExists(CloudFormationLintRule):
    """Check if Metadata Interface parameters exist"""
    id = 'W4001'
    shortdesc = 'Metadata Interface parameters exist'
    description = 'Metadata Interface parameters actually exist'
    tags = ['base', 'metadata']

    valid_keys = [
        'ParameterGroups',
        'ParameterLabels'
    ]

    def match(self, cfn):
        """Check CloudFormation Metadata Parameters Exist"""

        matches = list()

        strinterface = 'AWS::CloudFormation::Interface'
        parameters = cfn.get_parameter_names()
        metadata_obj = cfn.template.get('Metadata', {})
        if metadata_obj:
            interfaces = metadata_obj.get(strinterface, {})
            if isinstance(interfaces, dict):
                # Check Parameter Group Parameters
                paramgroups = interfaces.get('ParameterGroups', [])
                if isinstance(paramgroups, list):
                    for index, value in enumerate(paramgroups):
                        if 'Parameters' in value:
                            for paramindex, paramvalue in enumerate(value['Parameters']):
                                if paramvalue not in parameters:
                                    message = "Metadata Interface parameter doesn't exist {0}"
                                    matches.append(RuleMatch(
                                        ['Metadata', strinterface, 'ParameterGroups',
                                         index, 'Parameters', paramindex],
                                        message.format(paramvalue)
                                    ))
                paramlabels = interfaces.get('ParameterLabels', {})
                if isinstance(paramlabels, dict):
                    for param in paramlabels:
                        if param not in parameters:
                            message = "Metadata Interface parameter doesn't exist {0}"
                            matches.append(RuleMatch(
                                ['Metadata', strinterface, 'ParameterLabels', param],
                                message.format(param)
                            ))

        return matches
