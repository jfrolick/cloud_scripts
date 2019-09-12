#!/usr/bin/env python3

import json
import boto3
import sys
import re
import ipdb
import csv
import argparse
import os


#
# Parse arguments
#

parser = argparse.ArgumentParser(description='Remove tag from instances.')

parser.add_argument(
    '--tag',
    '-t',
    required=True,
    help='Tag to remove'
)

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
# Debug
#

if args.debug == True:
    print("Debugging console - loading ipdb.set_trace()")
    ipdb.set_trace()


#
# Map instance ID to name tag
#

print("Removing tags...")
for i in reservations:
    for j in i['Instances']:
        tags = flatten_tags(j['Tags'])
        if args.tag not in tags:
            continue
        # print('Removing ' + args.tag + ' from ' + j['InstanceId'])
        try:
            print('Removing ' + args.tag + ' from ' + j['InstanceId'])
            ec2.delete_tags(Resources=[j['InstanceId']],Tags=[{"Key": args.tag}])
        except ClientError as e:
            print("Unexpected error: %s" % e)
            exit(1)
print("Done.")

if args.debug == True:
    print("Debugging console - loading ipdb.set_trace()")
    ipdb.set_trace()
