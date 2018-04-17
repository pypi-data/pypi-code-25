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
    """Check if Parameters are configured correctly"""
    id = 'E2001'
    shortdesc = 'Parameters have appropriate properties'
    description = 'Making sure the parameters are properly configured'
    tags = ['base', 'parameters']

    valid_keys = [
        'AllowedPattern',
        'AllowedValues',
        'ConstraintDescription',
        'Default',
        'Description',
        'MaxLength',
        'MaxValue',
        'MinLength',
        'MinValue',
        'NoEcho',
        'Type'
    ]

    def match(self, cfn):
        """Check CloudFormation Parameters"""

        matches = list()

        for paramname, paramvalue in cfn.get_parameters().items():
            for propname, _ in paramvalue.items():
                if propname not in self.valid_keys:
                    message = "Parameter {0} has invalid property {1}"
                    matches.append(RuleMatch(
                        ['Parameters', paramname, propname],
                        message.format(paramname, propname)
                    ))

        return matches
