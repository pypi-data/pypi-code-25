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


class Required(CloudFormationLintRule):
    """Check Required Resource Configuration"""
    id = 'E3003'
    shortdesc = 'Required Resource Parameters are missing'
    description = 'Making sure that Resources properties ' + \
                  'that are required exist'
    tags = ['base', 'resources']

    def __init__(self):
        resourcespecs = cfnlint.helpers.load_resources()
        self.resourcetypes = resourcespecs['ResourceTypes']
        self.propertytypes = resourcespecs['PropertyTypes']

    def propertycheck(self, text, proptype, parenttype, resourcename, tree, root):
        """Check individual properties"""

        matches = list()
        if root:
            specs = self.resourcetypes
            resourcetype = parenttype
        else:
            specs = self.propertytypes
            resourcetype = str.format("{0}.{1}", parenttype, proptype)
            # handle tags
            if resourcetype not in specs:
                if proptype in specs:
                    resourcetype = proptype
                else:
                    resourcetype = str.format("{0}.{1}", parenttype, proptype)
            else:
                resourcetype = str.format("{0}.{1}", parenttype, proptype)

        resourcespec = specs[resourcetype]['Properties']

        for prop in resourcespec:
            if resourcespec[prop]['Required']:
                if prop not in text:
                    proptree = tree[:]
                    proptree.pop()
                    skip = False
                    if 'PrimitiveType' in specs[resourcetype]['Properties'][prop]:
                        if specs[resourcetype]['Properties'][prop]['PrimitiveType'] == 'Json':
                            skip = True
                        else:
                            message = "Property {0} missing from resource {1}"
                            matches.append(RuleMatch(proptree, message.format(prop, resourcename)))
                    if isinstance(text, dict) and not skip:
                        if not text:
                            message = "Property {0} missing from resource {1}"
                            matches.append(RuleMatch(proptree, message.format(prop, resourcename)))
                        for key in text:
                            if key in resourcespec:
                                arrproptree = tree[:]
                                arrproptree.append(key)
                                if key in cfnlint.helpers.CONDITION_FUNCTIONS:
                                    matches.extend(self.propertycheck(
                                        text[key][1], proptype,
                                        parenttype, resourcename, arrproptree, False))
                                    matches.extend(self.propertycheck(
                                        text[key][2], proptype,
                                        parenttype, resourcename, arrproptree, False))
                    else:
                        message = "Property {0} missing from resource {1}"
                        matches.append(RuleMatch(proptree, message.format(prop, resourcename)))
        for prop in text:
            proptree = tree[:]
            proptree.append(prop)
            if prop in resourcespec:
                if 'Type' in resourcespec[prop]:
                    if resourcespec[prop]['Type'] == 'List':
                        if 'PrimitiveItemType' not in resourcespec[prop]:
                            if isinstance(text[prop], list):
                                for index, item in enumerate(text[prop]):
                                    arrproptree = proptree[:]
                                    arrproptree.append(index)
                                    matches.extend(self.propertycheck(
                                        item, resourcespec[prop]['ItemType'],
                                        parenttype, resourcename, arrproptree, False))
                    else:
                        if resourcespec[prop]['Type'] not in ['Map']:
                            matches.extend(self.propertycheck(
                                text[prop], resourcespec[prop]['Type'],
                                parenttype, resourcename, proptree, False))

        return matches

    def match(self, cfn):
        """Check CloudFormation Properties"""
        matches = list()

        for resourcename, resourcevalue in cfn.get_resources().items():
            if 'Properties' in resourcevalue and 'Type' in resourcevalue:
                resourcetype = resourcevalue['Type']
                if resourcetype in self.resourcetypes:
                    tree = ['Resources', resourcename, 'Properties']
                    matches.extend(self.propertycheck(
                        resourcevalue['Properties'], '',
                        resourcetype, resourcename, tree, True))

        return matches
