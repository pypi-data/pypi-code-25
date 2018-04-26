import itertools
import boto3

class Route53Manager:

    def __init__(self, hosted_zone_id, url, aws_access_key=None, aws_secret_key=None):
        self.hosted_zone_id = hosted_zone_id

        if url.endswith('.'):
            self.url = url
        else:
            self.url = url + '.'   
        
        self.client = boto3.client('route53',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key)

    def create_record_sets(self, ips):
        alias_groups = self._list_alias_groups(details=True)
        alias_group_weights = map(lambda x: [x['AliasTarget']['DNSName'], x['Weight']], alias_groups)
        current_group_index = 0
        changes_list = []

        # If there are no alias group entries, fake the first one, with weight 0 and the
        # script will create the first one automatically.
        if not alias_group_weights:
            alias_group_weights = [[self._alias_group_name_from_index(1), 0]]

        for ip in ips:
            while alias_group_weights[current_group_index][1] >= 100:
                current_group_index += 1
                if current_group_index >= len(alias_group_weights):
                    new_alias_group_name = self._alias_group_name_from_index(current_group_index + 1)
                    alias_group_weights.append([new_alias_group_name, 0])

            alias_group_weights[current_group_index][1] += 1
            changes_list.append({
                            'Action': 'CREATE',
                            'ResourceRecordSet': {
                                'Name': alias_group_weights[current_group_index][0],
                                'Type': 'A',
                                'SetIdentifier': ip,
                                'Weight': 1,
                                'TTL': 10,
                                'ResourceRecords': [
                                    {
                                        'Value': ip
                                    },
                                ]
                            }
                        })
        
        for alias_group_weight in alias_group_weights:
            if alias_group_weight[1] > 0:
                changes_list.append({
                                    'Action': 'UPSERT',
                                    'ResourceRecordSet': {
                                        'Name': self.url,
                                        'Type': 'A',
                                        'SetIdentifier': alias_group_weight[0],
                                        'Weight': alias_group_weight[1],
                                        'AliasTarget': {
                                            'HostedZoneId': self.hosted_zone_id,
                                            'EvaluateTargetHealth': False,
                                            'DNSName': alias_group_weight[0]
                                        }
                                    }
                                })

        return self.client.change_resource_record_sets(
            HostedZoneId=self.hosted_zone_id,
            ChangeBatch= {
                            'Comment': 'Updating weighted DNS entries.',
                            'Changes': changes_list
            })

    def delete_record_sets(self, ips):
        existing_ips = self._list_ips()
        alias_groups = self._list_alias_groups(details=True)
        alias_group_weights = map(lambda x: [x['AliasTarget']['DNSName'], x['Weight']], alias_groups)
        alias_group_weights = filter(lambda x: x[1] > 0, alias_group_weights)

        ips_to_delete = []
        for ip in ips:
            matching_ip, alias_group_name = next(itertools.ifilter(lambda x: x[0] == ip, existing_ips), (None, None))
            if matching_ip:
                ips_to_delete.append((matching_ip, alias_group_name))
                alias_group_entry = next(itertools.ifilter(lambda x: x[0] == alias_group_name, alias_group_weights), None)
                if alias_group_entry:
                    alias_group_entry[1] = max(0, alias_group_entry[1] - 1)

        changes_list = []
        for alias_group_weight in alias_group_weights:
            changes_list.append({
                                'Action': 'UPSERT',
                                'ResourceRecordSet': {
                                    'Name': self.url,
                                    'Type': 'A',
                                    'SetIdentifier': alias_group_weight[0],
                                    'Weight': alias_group_weight[1],
                                    'AliasTarget': {
                                        'HostedZoneId': self.hosted_zone_id,
                                        'EvaluateTargetHealth': False,
                                        'DNSName': alias_group_weight[0]
                                    }
                                }
                            })
        for ip_to_delete in ips_to_delete:
            changes_list.append({
                                'Action': 'DELETE',
                                'ResourceRecordSet': {
                                    'Name': ip_to_delete[1],
                                    'Type': 'A',
                                    'SetIdentifier': ip_to_delete[0],
                                    'Weight': 1,
                                    'TTL': 10,
                                    'ResourceRecords': [
                                        {
                                            'Value': ip_to_delete[0]
                                        },
                                    ]
                                }
                            })

        return self.client.change_resource_record_sets(
            HostedZoneId=self.hosted_zone_id,
            ChangeBatch= {
                            'Comment': 'Updating weighted DNS entries.',
                            'Changes': changes_list
            })

    def _alias_group_name_from_index(self, index):
        parts = self.url.split('.')
        parts[0] = parts[0] + '-' + str(index)
        return '.'.join(parts)

    def _list_alias_groups(self, details=False):
        response = self.client.list_resource_record_sets(
            HostedZoneId=self.hosted_zone_id,
            StartRecordName=self.url,
            StartRecordType='A',
            MaxItems='100'
        )

        alias_group_records = filter(lambda x: x['Name'] == self.url, response['ResourceRecordSets'])
        
        if details:
            return alias_group_records

        alias_groups = map(lambda x: x['AliasTarget']['DNSName'], alias_group_records)
        return alias_groups

    def _list_record_sets(self, alias_group):
        alias_group_response = self.client.list_resource_record_sets(
            HostedZoneId=self.hosted_zone_id,
            StartRecordName=alias_group,
            StartRecordType='A',
            MaxItems='100'
        )
        return filter(lambda x: x['Name'] == alias_group, alias_group_response['ResourceRecordSets'])

    def _list_ips(self):
        alias_groups = self._list_alias_groups()

        ip_record_sets = []
        for alias_group in alias_groups:
            group_record_sets = self._list_record_sets(alias_group)
            ip_record_sets.extend(map(lambda x: (x['ResourceRecords'][0]['Value'], x['Name']),group_record_sets))
            
        return ip_record_sets
