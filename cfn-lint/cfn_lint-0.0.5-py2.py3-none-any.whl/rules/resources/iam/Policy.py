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


class Policy(CloudFormationLintRule):
    """Check if IAM Policy JSON is correct"""
    id = 'E2507'
    shortdesc = 'Check if IAM Policies are properly configured'
    description = 'See if there elements inside an IAM policy ' + \
                  'are correct'
    tags = ['base', 'properties', 'iam']

    def _check_policy_document(self, branch, policy):
        """Check policy document"""
        matches = list()

        valid_keys = [
            'Version',
            'Id',
            'Statement',
        ]

        if not isinstance(policy, dict):
            message = "IAM Policy Documents needs to be JSON"
            matches.append(
                RuleMatch(branch[:], message))
            return matches

        for parent_key, parent_value in policy.items():
            if parent_key not in valid_keys:
                message = "IAM Policy key %s doesn't exist." % (parent_key)
                matches.append(
                    RuleMatch(branch[:] + [parent_key], message))
            if parent_key == 'Statement':
                if isinstance(parent_value, (list)):
                    for index, statement in enumerate(parent_value):
                        matches.extend(
                            self._check_policy_statement(
                                branch[:] + [parent_key, index],
                                statement
                            )
                        )
                else:
                    message = "IAM Policy statement should be of list."
                    matches.append(
                        RuleMatch(branch[:] + [parent_key], message))
        return matches

    def _check_policy_statement(self, branch, statement):
        """Check statements"""
        matches = list()
        statement_valid_keys = [
            'Effect',
            'Principal',
            'NotPrincipal',
            'Action',
            'NotAction',
            'Resource',
            'NotResource',
            'Condition',
            'Sid',
        ]

        for key, _ in statement.items():
            if key not in statement_valid_keys:
                message = "IAM Policy statement key %s isn't valid" % (key)
                matches.append(
                    RuleMatch(branch[:] + [key], message))
        if 'Effect' not in statement:
            message = "IAM Policy statement missing Effect"
            matches.append(
                RuleMatch(branch[:], message))
        else:
            effect = statement.get('Effect')
            if effect not in ['Allow', 'Deny']:
                message = "IAM Policy Effect should be Allow or Deny"
                matches.append(
                    RuleMatch(branch[:] + ['Effect'], message))
        if 'Action' not in statement and 'NotAction' not in statement:
            message = "IAM Policy statement missing Action or NotAction"
            matches.append(
                RuleMatch(branch[:], message))
        if 'Principal' in statement:
            message = "IAM Policy statement shouldn't have Principal"
            matches.append(
                RuleMatch(branch[:] + ['Principal'], message))
        if 'NotPrincipal' in statement:
            message = "IAM Policy statement shouldn't have NotPrincipal"
            matches.append(
                RuleMatch(branch[:] + ['NotPrincipal'], message))
        if 'Resource' not in statement and 'NotResource' not in statement:
            message = "IAM Policy statement missing Resource or NotResource"
            matches.append(
                RuleMatch(branch[:], message))

        return(matches)

    def _check_policy(self, branch, policy):
        """Checks a policy"""
        matches = list()
        policy_document = policy.get('PolicyDocument', {})
        matches.extend(
            self._check_policy_document(
                branch + ['PolicyDocument'], policy_document))

        return matches

    def match(self, cfn):
        """Check IAM Policies Properties"""

        matches = list()

        iam_types = [
            'AWS::IAM::Group',
            'AWS::IAM::ManagedPolicy',
            'AWS::IAM::Policy',
            'AWS::IAM::Role',
            'AWS::IAM::User',
        ]

        resources = cfn.get_resources(iam_types)
        for resource_name, resource_values in resources.items():
            tree = ['Resources', resource_name, 'Properties']
            properties = resource_values.get('Properties', {})
            if properties:
                policy_document = properties.get('PolicyDocument', None)
                if policy_document:
                    matches.extend(
                        self._check_policy_document(
                            tree[:] + ['PolicyDocument'], policy_document))
                policy_documents = properties.get('Policies', [])
                for index, policy_document in enumerate(policy_documents):
                    matches.extend(
                        self._check_policy(
                            tree[:] + ['Policies', index],
                            policy_document))

        return matches
