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
import re
import six
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch
from cfnlint.parser import str_node, list_node


class RefExist(CloudFormationLintRule):
    """Check if Parameters are used"""
    id = 'E1012'
    shortdesc = 'Check if Refs exist'
    description = 'Making sure the refs exist'
    tags = ['base', 'functions', 'ref']

    pseudoparams = [
        'AWS::AccountId',
        'AWS::NotificationARNs',
        'AWS::NoValue',
        'AWS::Partition',
        'AWS::Region',
        'AWS::StackId',
        'AWS::StackName',
        'AWS::URLSuffix'
    ]

    def searchstring(self, string):
        """Search string for tokenized fields"""
        regex = re.compile(r'\${([a-zA-Z0-9]*)}')
        return regex.findall(string)

    def match(self, cfn):
        """Check CloudFormation Parameters"""

        matches = list()

        # Build the list of refs
        reftrees = cfn.search_deep_keys('Ref')
        refs = list()
        for reftree in reftrees:
            refs.append(reftree[-1])

        # build the sub lists
        subtrees = cfn.search_deep_keys('Fn::Sub')
        subs = list()
        for subtree in subtrees:
            subs.append(subtree[-1])

        valid_refs = cfn.get_valid_refs()

        # start with the basic ref calls
        for reftree in reftrees:
            ref = reftree[-1]
            if ref not in valid_refs:
                message = "Ref {0} not found as a resource or parameter"
                matches.append(RuleMatch(
                    reftree[:-2], message.format(ref)
                ))
        for subtree in subtrees:
            sub = subtree[-1]
            parammatches = []
            subparams = []
            if isinstance(sub, (six.text_type, str_node)):
                parammatches = self.searchstring(sub)
            elif isinstance(subtree[-1], (list, list_node)):
                if len(sub) == 2:
                    parammatches = self.searchstring(sub[0])
                    for subparam in sub[1]:
                        subparams.append(subparam)
            for parammatch in parammatches:
                if parammatch not in valid_refs:
                    if parammatch not in subparams:
                        message = "Ref {0} not found as a resource or parameter"
                        matches.append(RuleMatch(
                            subtree[:-2], message.format(parammatch)
                        ))

        return matches
