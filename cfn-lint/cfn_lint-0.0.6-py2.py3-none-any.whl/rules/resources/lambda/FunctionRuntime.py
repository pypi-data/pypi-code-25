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


class FunctionRuntime(CloudFormationLintRule):
    """Check if Lambda Function Memory Size"""
    id = 'E2531'
    shortdesc = 'Check Lambda Runtime Properties'
    description = 'See if Lambda Runtime is in valid'
    tags = ['base', 'resources', 'lambda']

    runtimes = [
        'nodejs', 'nodejs4.3', 'nodejs6.10', 'java8', 'python2.7', 'python3.6',
        'dotnetcore1.0', 'dotnetcore2.0', 'nodejs4.3-edge', 'go1.x'
    ]

    def check_value(self, value, path):
        """ Check runtime value """
        matches = list()

        message = "You must specify a valid value for runtime at {0}"

        if value not in self.runtimes:
            matches.append(RuleMatch(path, message.format(value, ('/'.join(path)))))

        return matches

    def check_ref(self, value, path, parameters, resources):
        """ Check Memory Size Ref """

        matches = list()
        if value in resources:
            message = "Runtime can't use a Ref to a resource for {0}"
            matches.append(RuleMatch(path, message.format(('/'.join(path)))))
        elif value in parameters:
            parameter = parameters.get(value, {})
            param_type = parameter.get('Type', '')
            allowed_values = parameter.get('AllowedValues', {})

            if param_type != 'String':
                param_path = ['Parameters', value, 'Type']
                message = "Type for Parameter should be String at {0}"
                matches.append(RuleMatch(param_path, message.format(('/'.join(param_path)))))

            if not allowed_values:
                param_path = ['Parameters', value]
                message = "Parameter should have allowed values at {0}"
                matches.append(RuleMatch(param_path, message.format(('/'.join(param_path)))))
            for index, allowed_value in enumerate(allowed_values):
                if allowed_value not in self.runtimes:
                    param_path = ['Parameters', value, 'AllowedValues', index]
                    message = "Allowed value should have proper types at {0}"
                    matches.append(RuleMatch(param_path, message.format(('/'.join(map(str, param_path))))))

        return matches

    def match(self, cfn):
        """Check Lambda Function Memory Size Resource Parameters"""

        matches = list()
        matches.extend(
            cfn.check_resource_property(
                'AWS::Lambda::Function', 'Runtime',
                check_value=self.check_value,
                check_ref=self.check_ref,
            )
        )

        return matches
