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
import six
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class GetAz(CloudFormationLintRule):
    """Check if GetAtt values are correct"""
    id = 'E1015'
    shortdesc = 'GetAz validation of parameters'
    description = 'Making sure the function not is of list'
    tags = ['base', 'functions', 'getaz']

    def match(self, cfn):
        """Check CloudFormation GetAz"""

        matches = list()

        getaz_objs = cfn.search_deep_keys('Fn::GetAZs')

        for getaz_obj in getaz_objs:
            getaz_value = getaz_obj[-1]
            if isinstance(getaz_value, six.string_types):
                if getaz_value != '' and getaz_value not in cfn.regions:
                    message = "GetAZs should be of empty or string of valid region for {0}"
                    matches.append(RuleMatch(
                        getaz_obj[:-1], message.format('/'.join(map(str, getaz_obj[:-1])))))
            elif isinstance(getaz_value, dict):
                if len(getaz_value) == 1:
                    if isinstance(getaz_value, dict):
                        for key, value in getaz_value.items():
                            if key != 'Ref' or value != 'AWS::Region':
                                message = "GetAZs should be of Ref to AWS::Region for {0}"
                                matches.append(RuleMatch(
                                    getaz_obj[:-1], message.format('/'.join(map(str, getaz_obj[:-1])))))
                    else:
                        message = "GetAZs should be of Ref to AWS::Region for {0}"
                        matches.append(RuleMatch(
                            getaz_obj[:-1], message.format('/'.join(map(str, getaz_obj[:-1])))))
                else:
                    message = "GetAZs should be of Ref to AWS::Region for {0}"
                    matches.append(RuleMatch(
                        getaz_obj[:-1], message.format('/'.join(map(str, getaz_obj[:-1])))))
        return matches
