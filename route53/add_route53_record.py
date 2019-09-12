#!/usr/bin/env python

import json
import boto3
import sys
import re
import ipdb
from botocore.exceptions import ClientError

client = boto3.client('route53')

hostedzones = client.list_hosted_zones_by_name(
        DNSName="sabrenow.com",
        MaxItems="10"
)

print hostedzones['DNSName']

for zone in hostedzones['HostedZones']:

    print zone['ResourceRecordSetCount']
    print zone['Config']['PrivateZone']
    print zone['Id']
    print zone['Name']

# print hostedzones['Config']['Comment']
#ipdb.set_trace()
