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


class Elb(CloudFormationLintRule):
    """Check if Elb Resource Properties"""
    id = 'E2503'
    shortdesc = 'Resource ELB Properties'
    description = 'See if Elb Resource Properties are set correctly \
HTTPS has certificate HTTP has no certificate'
    tags = ['base', 'properties', 'elb']

    def match(self, cfn):
        """Check ELB Resource Parameters"""

        matches = list()

        results = cfn.get_resource_properties(['AWS::ElasticLoadBalancingV2::Listener'])
        for result in results:
            protocol = result['Value'].get('Protocol')
            if protocol:
                if protocol not in ['HTTP', 'HTTPS', 'TCP']:
                    message = "Protocol is invalid for {0}"
                    path = result['Path'] + ['Protocol']
                    matches.append(RuleMatch(path, message.format(('/'.join(result['Path'])))))
                elif protocol in ['HTTPS']:
                    certificate = result['Value'].get('Certificates')
                    if not certificate:
                        message = "Certificates should be specified when using HTTPS for {0}"
                        path = result['Path'] + ['Protocol']
                        matches.append(RuleMatch(path, message.format(('/'.join(result['Path'])))))

        results = cfn.get_resource_properties(['AWS::ElasticLoadBalancing::LoadBalancer', 'Listeners'])
        for result in results:
            if isinstance(result['Value'], list):
                for index, listener in enumerate(result['Value']):
                    protocol = listener.get('Protocol')
                    if protocol:
                        if protocol not in ['HTTP', 'HTTPS', 'TCP', 'SSL']:
                            message = "Protocol is invalid for {0}"
                            path = result['Path'] + [index, 'Protocol']
                            matches.append(RuleMatch(path, message.format(('/'.join(result['Path'])))))
                        elif protocol in ['HTTPS', 'SSL']:
                            certificate = listener.get('SSLCertificateId')
                            if not certificate:
                                message = "Certificates should be specified when using HTTPS for {0}"
                                path = result['Path'] + [index, 'Protocol']
                                matches.append(RuleMatch(path, message.format(('/'.join(result['Path'])))))

        return matches
