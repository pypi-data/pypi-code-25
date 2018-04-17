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


class InstanceProfile(CloudFormationLintRule):
    """Check if IamInstanceProfile are used"""
    id = 'E2502'
    shortdesc = 'Check if IamInstanceProfile are using the name and not ARN'
    description = 'See if there are any properties IamInstanceProfile' + \
                  'are using name and not ARN'
    tags = ['base', 'properties']

    def match(self, cfn):
        """Check CloudFormation IamInstanceProfile Parameters"""

        matches = list()

        # Build the list of keys
        trees = cfn.search_deep_keys('Fn::GetAtt')
        # Filter only resoureces
        trees = filter(lambda x: x[0] == 'Resources', trees)
        for tree in trees:
            if any(e == 'IamInstanceProfile' for e in tree):
                obj = tree[-1]
                objtype = cfn.template.get('Resources', {}).get(obj[0], {}).get('Type')
                if objtype:
                    if objtype != 'AWS::IAM::InstanceProfile':
                        message = "Property IamInstanceProfile should relate to AWS::IAM::InstanceProfile for %s" % (
                            '/'.join(map(str, tree[:-1])))
                        matches.append(RuleMatch(tree[:-1], message))
                    else:
                        if obj[1] == 'Arn':
                            message = "Property IamInstanceProfile shouldn't be an ARN for %s" % (
                                '/'.join(map(str, tree[:-1])))
                            matches.append(RuleMatch(tree[:-1], message))

        # Search Refs
        trees = cfn.search_deep_keys('Ref')
        # Filter only resoureces
        trees = filter(lambda x: x[0] == 'Resources', trees)
        for tree in trees:
            if any(e == 'IamInstanceProfile' for e in tree):
                obj = tree[-1]
                objtype = cfn.template.get('Resources', {}).get(obj, {}).get('Type')
                if objtype:
                    if objtype != 'AWS::IAM::InstanceProfile':
                        message = "Property IamInstanceProfile should relate to AWS::IAM::InstanceProfile for %s" % (
                            '/'.join(map(str, tree[:-1])))
                        matches.append(RuleMatch(tree[:-1], message))

        return matches
