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


class ImageId(CloudFormationLintRule):
    """Check if Parameters are used"""
    id = 'W2506'
    shortdesc = 'Check if ImageId Parameters have the correct type'
    description = 'See if there are any refs for ImageId to a parameter ' + \
                  'of innapropriate type (not AWS::EC2::Image::Id)'
    tags = ['base', 'parameters', 'imageid']

    def match(self, cfn):
        """Check CloudFormation ImageId Parameters"""

        matches = list()

        # Build the list of refs
        imageidtrees = cfn.search_deep_keys('ImageId')
        valid_refs = cfn.get_valid_refs()
        # Filter only resoureces
        imageidtrees = [x for x in imageidtrees if x[0] == 'Resources']
        for imageidtree in imageidtrees:
            imageidobj = imageidtree[-1]
            if isinstance(imageidobj, dict):
                if len(imageidobj) == 1:
                    for key, paramname in imageidobj.items():
                        if key == 'Ref':
                            if paramname in valid_refs:
                                if valid_refs[paramname]['Type'] != 'AWS::EC2::Image::Id':
                                    message = "Parameter %s should be of type \
AWS::EC2::Image::Id" % (paramname)
                                    tree = ['Parameters', paramname]
                                    matches.append(RuleMatch(tree, message))
                else:
                    message = "Innappropriate map found for imageid on %s" % (
                        '/'.join(map(str, imageidtree[:-1])))
                    matches.append(RuleMatch(imageidtree[:-1], message))

        return matches
