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


class Not(CloudFormationLintRule):
    """Check if Not values are correct"""
    id = 'E1023'
    shortdesc = 'Validation NOT function configuration'
    description = 'Making sure that NOT functions are list'
    tags = ['base', 'functions', 'not']

    def match(self, cfn):
        """Check CloudFormation GetAtt"""

        matches = list()

        fnnots = cfn.search_deep_keys('Fn::Not')
        for fnnot in fnnots:
            if not isinstance(fnnot[-1], list):
                message = "Function Not {0} should be a list"
                matches.append(RuleMatch(fnnot, message.format('/'.join(map(str, fnnot[:-2])))))

        return matches
