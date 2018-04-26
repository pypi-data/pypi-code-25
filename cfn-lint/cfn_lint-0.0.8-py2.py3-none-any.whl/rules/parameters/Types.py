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


class Types(CloudFormationLintRule):
    """Check if Parameters are typed"""
    id = 'E2002'
    shortdesc = 'Parameters have appropriate type'
    description = 'Making sure the parameters have a correct type'
    tags = ['base', 'parameters']

    valid_types = [
        'String',
        'Number',
        'List<Number>',
        'CommaDelimitedList',
        'AWS::EC2::AvailabilityZone::Name',
        'AWS::EC2::Image::Id',
        'AWS::EC2::Instance::Id',
        'AWS::EC2::KeyPair::KeyName',
        'AWS::EC2::SecurityGroup::GroupName',
        'AWS::EC2::SecurityGroup::Id',
        'AWS::EC2::Subnet::Id',
        'AWS::EC2::Volume::Id',
        'AWS::EC2::VPC::Id',
        'AWS::Route53::HostedZone::Id',
        'List<AWS::EC2::AvailabilityZone::Name>',
        'List<AWS::EC2::Image::Id>',
        'List<AWS::EC2::Instance::Id>',
        'List<AWS::EC2::SecurityGroup::GroupName>',
        'List<AWS::EC2::SecurityGroup::Id>',
        'List<AWS::EC2::Subnet::Id>',
        'List<AWS::EC2::Volume::Id>',
        'List<AWS::EC2::VPC::Id>',
        'List<AWS::Route53::HostedZone::Id>',
        'AWS::SSM::Parameter::Name'
    ]

    def match(self, cfn):
        """Check CloudFormation Parameters"""

        matches = list()

        for paramname, paramvalue in cfn.get_parameters().items():
            # If the type isn't found we create a valid one
            # this test isn't about missing required properties for a
            # parameter.
            paramtype = paramvalue.get('Type', 'String')
            if paramtype not in self.valid_types:
                if not paramtype.startswith('AWS::SSM::Parameter::Value'):
                    message = "Parameter {0} has invalid type {1}"
                    matches.append(RuleMatch(
                        ['Parameters', paramname, 'Type'],
                        message.format(paramname, paramtype)
                    ))

        return matches
