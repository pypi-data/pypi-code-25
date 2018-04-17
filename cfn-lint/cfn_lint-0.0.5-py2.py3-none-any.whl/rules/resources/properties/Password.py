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


class Password(CloudFormationLintRule):
    """Check if Password Properties are properly configured"""
    id = 'E2501'
    shortdesc = 'Check if Password Properties are correctly configured'
    description = 'Password properties should be strings and if parameter using NoEcho'
    tags = ['base', 'parameters', 'passwords']

    def match(self, cfn):
        """Check CloudFormation Password Parameters"""

        matches = list()
        password_properties = ['Password', 'DbPassword', 'MasterUserPassword']

        parameters = cfn.get_parameter_names()
        fix_params = set()
        for password_property in password_properties:
            # Build the list of refs
            trees = cfn.search_deep_keys(password_property)
            trees = [x for x in trees if x[0] == 'Resources']
            for tree in trees:
                obj = tree[-1]
                if isinstance(obj, six.text_type):
                    message = "Password shouln't be hardcoded for %s" % (
                        '/'.join(map(str, tree[:-1])))
                    matches.append(RuleMatch(tree[:-1], message))
                elif isinstance(obj, dict):
                    if len(obj) == 1:
                        for key, value in obj.items():
                            if key == 'Ref':
                                if value in parameters:
                                    param = cfn.template['Parameters'][value]
                                    if 'NoEcho' in param:
                                        if not param['NoEcho']:
                                            fix_params.add(value)
                                    else:
                                        fix_params.add(value)
                    else:
                        message = "Innappropriate map found for password on %s" % (
                            '/'.join(map(str, tree[:-1])))
                        matches.append(RuleMatch(tree[:-1], message))

        for paramname in fix_params:
            message = "Parameter %s should have NoEcho True" % (paramname)
            tree = ['Parameters', paramname]
            matches.append(RuleMatch(tree, message))
        return matches
