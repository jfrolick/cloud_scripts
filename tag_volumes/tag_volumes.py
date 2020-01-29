#!/usr/bin/env python3

import json
import boto3
import sys
import re
import ipdb
import argparse
import os


allowedtags = [
    'Name',
    'Owner',
    'BusinessUnit',
    'BusinessService',
    'TechnicalService',
    'Environment',
    'ContactEmail',
    'Hostname'
]


#
# Parse arguments
#

parser = argparse.ArgumentParser(description='Tag instances.')

parser.add_argument(
    '--region',
    '-r',
    default='us-east-1',
    help='AWS region name'
)

parser.add_argument(
    '--debug',
    '-d',
    default=False,
    help="Debug",
    dest='debug',
    action='store_true'
)

args = parser.parse_args()

if args.region:
    os.environ['DEFAULT_AWS_REGION'] = args.region

print("AWS Region: " + os.environ['DEFAULT_AWS_REGION'])


#
# Connect to AWS
#

#ec2 = boto3.resource('ec2', region_name='us-east-1')

ec2 = boto3.client('ec2')

print("Describing instances.")
try:
    reservations = ec2.describe_instances().get(
        'Reservations', []
        )
except ClientError as e:
    print("Unexpected error: %s" % e)
    exit(1)

print("Done.")


if args.debug == True:
    print("Debugging console - loading ipdb.set_trace()")
    ipdb.set_trace()


#
# Flatten tags function
#

def flatten_tags(tags):

    flattened = {}

    if len(tags) < 1:
        return None

    for i in tags:
        flattened[i['Key']] = i['Value']

    return flattened


for r in reservations:
    for i in r['Instances']:
        # ipdb.set_trace()
        tags = flatten_tags(i['Tags'])
        newtags = []
        if 'Name' not in tags:
            print("Skipping Instance" + ' ' + i['InstanceId'])
            continue
        # print (i)
        # print (i['Tags'])
        for b in i['BlockDeviceMappings']:
            print (i['InstanceId'] + ' ' + b['DeviceName'] + " " + b['Ebs']['VolumeId'] + " " + b['Ebs']['Status'])
            for key, value in tags.items():
                if key not in allowedtags:
                    continue
                if key == 'Name':
                    device = re.sub("\/dev\/",'',b['DeviceName'])
                    print ("Adding: " + key + ": " + value + "-" + device)
                    newtags
                else:
                    print ("Adding: " + key + ": " + value)
