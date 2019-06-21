#!/usr/bin/env python

import json
import boto3
import sys
import re
import ipdb


#ec2 = boto3.resource('ec2', region_name='us-east-1')

client = boto3.client('ec2')

# Get instances
reservations = client.describe_instances().get(
        'Reservations', []
)

#ipdb.set_trace()

def flatten_tags(tags):

    flattened = {}

    if len(tags) < 1:
        return None

    for i in tags:
        flattened[i['Key']] = i['Value']

    return flattened

ipdb.set_trace()

#for i in reservations:
#    for j in i['Instances']:
        # ipdb.set_trace()
        # print j['InstanceId']
