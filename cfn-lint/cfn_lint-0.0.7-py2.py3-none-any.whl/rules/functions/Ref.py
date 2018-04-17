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


class Ref(CloudFormationLintRule):
    """Check if Ref value is a string"""
    id = 'E1020'
    shortdesc = 'Ref validation of value'
    description = 'Making the Ref has a value of String (no other functions are supported)'
    tags = ['base', 'functions', 'ref']

    def match(self, cfn):
        """Check CloudFormation Ref"""

        matches = list()

        ref_objs = cfn.search_deep_keys('Fn::Ref')

        for ref_obj in ref_objs:
            value = ref_obj[-1]
            if not isinstance(value, six.string_types):
                message = "Ref can only be a string for {0}"
                matches.append(RuleMatch(ref_obj[:-1], message.format('/'.join(map(str, ref_obj[:-1])))))

        return matches
