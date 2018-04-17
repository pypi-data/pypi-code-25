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
import cfnlint.helpers


class Exclusive(CloudFormationLintRule):
    """Check Properties Resource Configuration"""
    id = 'E2520'
    shortdesc = 'Check Properties that are mutually exclusive'
    description = 'Making sure CloudFormation properties ' + \
                  'that are exclusive are not defined'
    tags = ['base', 'resources']

    def __init__(self):
        """Init"""
        self.exlusivespec = cfnlint.helpers.load_resources('data/ResourcePropertiesExclusive.json')

    def match(self, cfn):
        """Check CloudFormation Properties"""
        matches = list()

        for excl_type, excl_values in self.exlusivespec.items():
            for res_name, res_value in cfn.get_resources(excl_type).items():
                for excl_name, excl_value in excl_values.items():
                    properties = res_value.get('Properties', {})
                    if excl_name in properties:
                        for prop_name in excl_value:
                            if prop_name in res_value['Properties']:
                                message = "Parameter {0} shouldn't exist with {1} for {2}"
                                matches.append(RuleMatch(
                                    ['Resources', res_name, 'Properties', excl_name],
                                    message.format(excl_name, prop_name, res_name)
                                ))

        return matches
