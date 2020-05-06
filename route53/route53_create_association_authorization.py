#!/usr/bin/env python3

import json
import boto3
import sys
import re
import ipdb
import os
import argparse
from botocore.exceptions import ClientError


client = boto3.client('route53')

parser = argparse.ArgumentParser(description='Create Route53peering association authorization')

parser.add_argument(
    '--zone',
    '-z',
    help='Route53 Zone ID',
)

parser.add_argument(
    '--region',
    '-r',
    help='AWS Region'
)

parser.add_argument(
    '--vpc',
    '-v',
    help='Remote VPC ID',
)

parser.add_argument(
    '--list',
    '-l',
    help='List Zones',
    action='store_true'
)

args = parser.parse_args()

if args.region:
    os.environ['DEFAULT_AWS_REGION'] = args.region


if args.list:

    hostedzones = client.list_hosted_zones_by_name()

    print ("Private Zones:\n")

    for zone in hostedzones['HostedZones']:

        if zone['Config']['PrivateZone']:
            print (zone['Name'], "\t", zone['Id'])

    sys.exit(0)

else:

    if not args.zone:
        parser.print_help()
        print ("\nError:\n  --zone is a required argument")
        sys.exit(1)
    if not args.vpc:
        parser.print_usage()
        print ("\nError:\n  --vpc is a required argument")
        sys.exit(1)
    if 'DEFAULT_AWS_REGION' not in os.environ:
        parser.print_usage()
        print ("\nError:\n  --region is a required argument")
        sys.exit(1)

    print ("Zone:   ", args.zone)
    print ("VPCId:  ", args.vpc)
    print ("Region: ", args.region)


try:
    response = client.create_vpc_association_authorization(
        HostedZoneId=args.zone,
        VPC={
            'VPCRegion': args.region,
            'VPCId': args.vpc
        }
    )
except ClientError as e:
    print ("Unexpected error: %s" % e)
    sys.exit(1)

print(response)
