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
from cfnlint.helpers import load_resources


class Value(CloudFormationLintRule):
    """Check if Outputs have string values"""
    id = 'E6003'
    shortdesc = 'Outputs have values of strings'
    description = 'Making sure the outputs have strings as values'
    tags = ['base', 'outputs']

    def __init__(self):
        resourcespecs = load_resources()
        self.resourcetypes = resourcespecs['ResourceTypes']

    def match(self, cfn):
        """Check CloudFormation Outputs"""

        matches = list()

        template = cfn.template

        getatts = cfn.search_deep_keys('Fn::GetAtt')
        refs = cfn.search_deep_keys('Ref')
        # If using a getatt make sure the attribute of the resource
        # is not of Type List
        for getatt in getatts:
            if getatt[0] == 'Outputs':
                if getatt[2] == 'Value':
                    obj = getatt[-1]
                    if isinstance(obj, list):
                        objtype = template.get('Resources', {}).get(obj[0], {}).get('Type')
                        if objtype:
                            attribute = self.resourcetypes.get(
                                objtype, {}).get('Attributes', {}).get(obj[1], {}).get('Type')
                            if attribute == 'List':
                                if getatt[-4] != 'Fn::Join' and getatt[-3] != 1:
                                    message = "Output {0} value {1} is of type list"
                                    matches.append(RuleMatch(
                                        getatt,
                                        message.format(getatt[1], '/'.join(obj))
                                    ))

        # If using a ref for an output make sure it isn't a
        # Parameter of Type List
        for ref in refs:
            if ref[0] == 'Outputs':
                if ref[2] == 'Value':
                    obj = ref[-1]
                    if isinstance(obj, six.string_types):
                        param = template.get('Parameters', {}).get(obj)
                        if param:
                            paramtype = param.get('Type')
                            if paramtype:
                                if paramtype.startswith('List<'):
                                    if ref[-4] != 'Fn::Join' and ref[-3] != 1:
                                        message = "Output {0} value {1} is of type list"
                                        matches.append(RuleMatch(
                                            ref,
                                            message.format(ref[1], obj)
                                        ))

        return matches
