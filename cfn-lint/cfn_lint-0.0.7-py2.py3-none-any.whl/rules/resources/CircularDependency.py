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
from cfnlint.parser import str_node


class CircularDependency(CloudFormationLintRule):
    """Check if Resources have a circular dependency"""
    id = 'E3004'
    shortdesc = 'Resource dependencies are not circular'
    description = 'Check that Resources are not circularly dependent ' \
                  'by Ref, Sub, or GetAtt'
    tags = ['base', 'resources', 'circularly']

    def searchstring(self, string):
        """Search string for tokenized fields"""
        regex = re.compile(r'\${([a-zA-Z0-9.]*)}')
        return regex.findall(string)

    def match(self, cfn):
        """Check CloudFormation Resources"""

        matches = list()

        ref_objs = cfn.search_deep_keys('Ref')

        resources = {}
        for ref_obj in ref_objs:
            value = ref_obj[-1]
            ref_type, ref_name = ref_obj[:2]
            if ref_type == 'Resources':
                if cfn.template.get('Resources', {}).get(value, {}):
                    if not resources.get(ref_name):
                        resources[ref_name] = []
                    resources[ref_name].append(value)
                    if ref_name in resources.get(value, []) or ref_name == value:
                        message = "Refs cannot create circular dependencies on resources for {0}"
                        matches.append(RuleMatch(ref_obj, message.format('/'.join(map(str, ref_obj)))))

        getatt_objs = cfn.search_deep_keys('Fn::GetAtt')
        for getatt_obj in getatt_objs:
            value = getatt_obj[-1]
            if not isinstance(value, list):
                continue
            if not len(value) == 2:
                continue
            ref_name = value[0]
            res_type, res_name = getatt_obj[:2]
            if res_type == 'Resources':
                if cfn.template.get('Resources', {}).get(ref_name, {}):
                    if not resources.get(res_name):
                        resources[res_name] = []
                    resources[res_name].append(ref_name)
                    if res_name in resources.get(ref_name, []) or ref_name == res_name:
                        path_error = getatt_obj[:-1]
                        message = "GetAtt cannot create circular dependencies on resources for {0}"
                        matches.append(RuleMatch(path_error, message.format('/'.join(map(str, path_error)))))

        sub_objs = cfn.search_deep_keys('Fn::Sub')
        sub_parameter_values = {}
        for sub_obj in sub_objs:
            value = sub_obj[-1]
            res_type, res_name = sub_obj[:2]
            if isinstance(value, list):
                if not value:
                    continue
                if len(value) == 2:
                    sub_parameter_values = value[1]
                sub_parameters = self.searchstring(value[0])
            elif isinstance(value, (six.text_type, str_node)):
                sub_parameters = self.searchstring(value)

            for sub_parameter in sub_parameters:
                if sub_parameter not in sub_parameter_values:
                    if '.' in sub_parameter:
                        sub_parameter = sub_parameter.split('.')[0]
                    if cfn.template.get('Resources', {}).get(sub_parameter, {}):
                        if not resources.get(res_name):
                            resources[res_name] = []
                        resources[res_name].append(sub_parameter)
                        if res_name in resources.get(sub_parameter, []) or res_name == sub_parameter:
                            path_error = sub_obj[:-1]
                            message = "GetAtt cannot create circular dependencies on resources for {0}"
                            matches.append(RuleMatch(path_error, message.format('/'.join(map(str, path_error)))))

        return matches
