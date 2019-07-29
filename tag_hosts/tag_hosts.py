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

parser = argparse.ArgumentParser(description='Tag instances.')

parser.add_argument(
    '--input',
    '-i',
    required=True,
    help='Input file name'
)

parser.add_argument(
    '--region',
    '-r',
    default='us-east-1',
    help='AWS region name'
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


# Debug
#ipdb.set_trace()


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

# Debug
#ipdb.set_trace()


#
# Map instance ID to name tag
#

print("Parsing tags...")
db = {}
for i in reservations:
    for j in i['Instances']:
        # ipdb.set_trace()
        tags = flatten_tags(j['Tags'])
        if 'Name' not in tags:
            continue
        # print(j['InstanceId'] + ' ' + tags['Name'])
        db[tags['Name']] = j['InstanceId']

print("Done.")


#
# Process the csv file containing host names and tags
#

try:
    with open(args.input, newline='') as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            if row[2] in db:
                print("Tagging: " + row[2] + " " + db[row[2]] +
                      " BusinessUnit as " + row[1])
                try:
                    ec2.create_tags(Resources=[db[row[2]]], Tags=[{'Key':'Business Unit', 'Value':row[1]}])
                except ClientError as e:
                    print("Unexpected error: %s" % e)
                    exit(1)
            else:
                print("Entry not found: " + row[2])
except (FileNotFoundError, IOError, OSError):
    print("Error opening file.")
    exit(1)

# Debug
#ipdb.set_trace()
