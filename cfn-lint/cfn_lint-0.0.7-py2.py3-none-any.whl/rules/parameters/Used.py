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
from __future__ import unicode_literals
import re
import six
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch
from cfnlint.parser import str_node


class Used(CloudFormationLintRule):
    """Check if Parameters are used"""
    id = 'W2001'
    shortdesc = 'Check if Parameters are Used'
    description = 'Making sure the parameters defined are used'
    tags = ['base', 'parameters']

    def searchstring(self, string, parameter):
        """Search string for tokenized fields"""
        regex = re.compile(r'\${(%s)}' % parameter)
        return regex.findall(string)

    def isparaminref(self, subs, parameter):
        """Search sub strings for paramters"""
        for sub in subs:
            if isinstance(sub, (six.text_type, str_node)):
                if self.searchstring(sub, parameter):
                    return True

        return False

    def match(self, cfn):
        """Check CloudFormation Parameters"""

        matches = list()

        reftrees = cfn.search_deep_keys('Ref')
        refs = list()
        for reftree in reftrees:
            refs.append(reftree[-1])
        subtrees = cfn.search_deep_keys('Fn::Sub')
        subs = list()
        for subtree in subtrees:
            if isinstance(subtree[-1], list):
                subs.append(subtree[-1][0])
            else:
                subs.append(subtree[-1])
        for paramname, _ in cfn.get_parameters().items():
            if paramname not in refs:
                if not self.isparaminref(subs, paramname):
                    message = "Parameter {0} not used."
                    matches.append(RuleMatch(
                        ['Parameters', paramname],
                        message.format(paramname)
                    ))

        return matches
