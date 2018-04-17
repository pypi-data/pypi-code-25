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


class GetAtt(CloudFormationLintRule):
    """Check if GetAtt values are correct"""
    id = 'E1010'
    shortdesc = 'GetAtt validation of parameters'
    description = 'Making sure the function GetAtt is of list'
    tags = ['base', 'functions', 'getatt']

    def __init__(self):
        resourcespecs = cfnlint.helpers.load_resources()
        self.resourcetypes = resourcespecs['ResourceTypes']
        self.propertytypes = resourcespecs['PropertyTypes']

    def match(self, cfn):
        """Check CloudFormation GetAtt"""

        matches = list()

        getatts = cfn.search_deep_keys('Fn::GetAtt')
        valid_getatts = cfn.get_valid_getatts()
        for getatt in getatts:
            if len(getatt[-1]) < 2:
                message = "Invalid GetAtt for {0}"
                matches.append(RuleMatch(getatt, message.format('/'.join(map(str, getatt[:-1])))))
                continue
            resname = getatt[-1][0]
            restype = '.'.join(getatt[-1][1:])
            if resname in valid_getatts:
                if restype not in valid_getatts[resname] and '*' not in valid_getatts[resname]:
                    message = "Invalid GetAtt {0}.{1} for resource {2}"
                    matches.append(RuleMatch(
                        getatt[:-1], message.format(resname, restype, getatt[1])))
            else:
                message = "Invalid GetAtt {0}.{1} for resource {2}"
                matches.append(RuleMatch(getatt, message.format(resname, restype, getatt[1])))

        return matches
