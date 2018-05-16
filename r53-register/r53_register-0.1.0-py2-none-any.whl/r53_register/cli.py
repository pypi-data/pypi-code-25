from __future__ import print_function
from random import shuffle

import boto3
import botocore
import netifaces
import os
import requests
import sys

if len(sys.argv) < 2:
    print('No DNS address given.', file=sys.stderr)
    exit(1)

dns = sys.argv[1]

public = os.environ.get('PUBLIC_IP', False)

if public:

    public_ip_urls = [
        'http://icanhazip.com',
        'http://myip.dnsomatic.com/'
    ]
    shuffle(public_ip_urls)

    for url in public_ip_urls:
        try:
            ip = requests.get(url).text.rstrip()
            break
        except:
            continue

else:

    prefix_list = os.environ.get("INTERFACE_PREFIX", "en,eth,wl")
    prefixes = prefix_list.split(',')

    interface = os.environ.get("INTERFACE_NAME", None)

    if not interface:
        interfaces = []

        for prefix in prefixes:
            for i in netifaces.interfaces():
                if i.startswith(prefix):
                    interfaces.append(i)
                    break

        if len(interfaces) == 0:
            print('No interface found.', file=sys.stderr)
            exit(1)

        interface = interfaces[0]

    ip = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']

client = boto3.client('route53')

zone_name = ''
zone_id = None
hosted_zones = client.list_hosted_zones_by_name()['HostedZones']

for zone in hosted_zones:
    name = zone['Name'][:-1]
    if dns.endswith(name) and len(name) > len(zone_name):
        zone_name = name
        zone_id = zone['Id'].split('/')[-1]

if not zone_id:
    print('No zone found.', file=sys.stderr)
    exit(1)

def main():
    try:
        client.change_resource_record_sets(
            HostedZoneId=zone_id,
            ChangeBatch={
                'Comment': '%s -> %s' % (dns, ip),
                'Changes': [
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': dns,
                            'Type': 'A',
                            'TTL': 30,
                            'ResourceRecords': [
                                {
                                    'Value': ip
                                }
                            ]
                        }
                    }
                ]
            }
        )
    except:
        print('DNS record update failed.', file=sys.stderr)
        exit(1)

    print('Updated %s -> %s.' % (dns, ip))
    exit(0)
