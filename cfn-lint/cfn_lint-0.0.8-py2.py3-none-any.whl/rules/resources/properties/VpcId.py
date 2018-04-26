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


class VpcId(CloudFormationLintRule):
    """Check if VPC Parameters are of correct type"""
    id = 'W2505'
    shortdesc = 'Check if VpcID Parameters have the correct type'
    description = 'See if there are any refs for VpcId to a parameter ' + \
                  'of innapropriate type (not AWS::EC2::VPC::Id)'
    tags = ['base', 'parameters', 'vpcid']

    def match(self, cfn):
        """Check CloudFormation VpcId Parameters"""

        matches = list()

        # Build the list of refs
        trees = cfn.search_deep_keys('VpcId')
        parameters = cfn.get_parameter_names()
        correct_type = 'AWS::EC2::VPC::Id'
        fix_param_types = set()
        trees = [x for x in trees if x[0] == 'Resources']
        for tree in trees:
            obj = tree[-1]
            if isinstance(obj, dict):
                if len(obj) == 1:
                    for key in obj:
                        if key == 'Ref':
                            paramname = obj[key]
                            if paramname in parameters:
                                param = cfn.template['Parameters'][paramname]
                                if 'Type' in param:
                                    paramtype = param['Type']
                                    if paramtype != correct_type:
                                        fix_param_types.add(paramname)
                else:
                    message = "Innappropriate map found for vpcid on %s" % (
                        '/'.join(map(str, tree[:-1])))
                    matches.append(RuleMatch(tree[:-1], message))

        for paramname in fix_param_types:
            message = "Parameter %s should be of type %s" % (paramname, correct_type)
            tree = ['Parameters', paramname]
            matches.append(RuleMatch(tree, message))
        return matches
