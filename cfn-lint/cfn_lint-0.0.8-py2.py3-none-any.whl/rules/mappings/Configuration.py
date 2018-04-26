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
    """Check if Mappings are configured correctly"""
    id = 'E7001'
    shortdesc = 'Mappings are appropriately configured'
    description = 'Check if Mappings are properly configured'
    tags = ['base', 'mappings']

    def match(self, cfn):
        """Check CloudFormation Parameters"""

        matches = list()

        mappings = cfn.template.get('Mappings', {})
        if mappings:
            for mapname, mapobj in mappings.items():
                if not isinstance(mapobj, dict):
                    message = "Mapping {0} has invalid property"
                    matches.append(RuleMatch(
                        ['Mappings', mapname],
                        message.format(mapname)
                    ))
                else:
                    for firstkey in mapobj:
                        firstkeyobj = mapobj[firstkey]
                        if not isinstance(firstkeyobj, dict):
                            message = "Mapping {0} has invalid property at {1}"
                            matches.append(RuleMatch(
                                ['Mappings', mapname, firstkey],
                                message.format(mapname, firstkeyobj)
                            ))
                        else:
                            for secondkey in firstkeyobj:
                                if isinstance(firstkeyobj[secondkey], (dict, list)):
                                    message = "Mapping {0} has invalid property at {1}"
                                    matches.append(RuleMatch(
                                        ['Mappings', mapname, firstkey, secondkey],
                                        message.format(mapname, secondkey)
                                    ))

        return matches
