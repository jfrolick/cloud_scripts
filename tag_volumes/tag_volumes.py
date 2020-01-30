#!/usr/bin/env python3

import json
import boto3
import sys
import re
import ipdb
import argparse
import os


copytags = [
    'Name',
    'Owner',
    'BusinessUnit',
    'BusinessService',
    'TechnicalService',
    'Environment',
    'ContactEmail',
    'Hostname'
]

dryrun = False


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


#
# Loop through reservations
#

for r in reservations:

    for i in r['Instances']:

        # ipdb.set_trace()

        tags = flatten_tags(i['Tags'])
        newtags = []

        print ('Instance: ' + i['InstanceId'])

        if 'Name' not in tags:
            print("Skipping Instance" + ' ' + i['InstanceId'])
            continue

        for b in i['BlockDeviceMappings']:

            print ('  Tagging: ' + b['Ebs']['VolumeId'] + ' ' + b['DeviceName'])

            # for key, value in tags.items():
            #     if key not in copytags:
            #         continue
            #     if key == 'Name':
            #         device = re.sub("\/dev\/",'',b['DeviceName'])
            #         print ("Adding: " + key + ": " + value + "-" + device)
            #         newtags
            #     else:
            #         print ("Adding: " + key + ": " + value)

            for t in i['Tags']:

                key = re.sub(' ','',t['Key'])

                if key not in copytags:
                    continue

                if key == 'Name':
                    device = re.sub("\/dev\/",'',b['DeviceName'])
                    # print ("Adding: " + key + ": " + t['Value'] + "-" + device)
                    value = t['Value'] + "-" + device
                else:
                    # print ("Adding: " + key + ": " + t['Value'])
                    value = t['Value']

                newtags.append(
                    {
                        'Key': key,
                        'Value': value
                    }
                )

            try:
                response = ec2.create_tags(
                    DryRun = dryrun,
                    Resources = [ b['Ebs']['VolumeId'] ],
                    Tags = newtags
                )

            except Exception as e:
                print("Unexpected error: %s" % e)
                exit(1)
