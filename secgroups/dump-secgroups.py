#!/usr/bin/env python3

import json
import boto3
import sys
import re
import ipdb
import os
from botocore.exceptions import ClientError


# Get the region from environment variable
region = os.getenv('AWS_DEFAULT_REGION')

# Connect to AWS
ec2 = boto3.client('ec2', region_name=region)

# Get the security groups
try:
    secgroups = ec2.describe_security_groups()
except ClientError as e:
    print(e)


# Loop through groups

for group in secgroups['SecurityGroups']:

    empty = True

    # Ingress rules
    for ippermission in group['IpPermissions']:

        if ippermission['IpProtocol'] == "tcp":
            protocol = ippermission['IpProtocol']
            fromport = ippermission['FromPort']
            toport = ippermission['ToPort']
        elif ippermission['IpProtocol'] == "-1":
            protocol = "all"
            fromport = "0"
            toport = "65535"

        for rule in ippermission['UserIdGroupPairs']:
            empty = False
            print(
                "Ingress: ",
                group['GroupId'],
                group['GroupName'],
                group['VpcId'],
                protocol,
                fromport,
                toport,
                rule['GroupId'],
                rule['UserId']
            )

        for rule in ippermission['IpRanges']:
            empty = False
            print(
                "Ingress: ",
                group['GroupId'],
                group['GroupName'],
                group['VpcId'],
                protocol,
                fromport,
                toport,
                rule['CidrIp'],
            )


    # Egress rules

    for ippermission in group['IpPermissionsEgress']:

        if ippermission['IpProtocol'] == "tcp":
            protocol = ippermission['IpProtocol']
            fromport = ippermission['FromPort']
            toport = ippermission['ToPort']
        elif ippermission['IpProtocol'] == "-1":
            protocol = "all"
            fromport = "0"
            toport = "65535"

        for rule in ippermission['UserIdGroupPairs']:
            empty = False
            print(
                "Egress: ",
                group['GroupId'],
                group['GroupName'],
                group['VpcId'],
                protocol,
                fromport,
                toport,
                rule['GroupId'],
                rule['UserId']
            )

        for rule in ippermission['IpRanges']:
            empty = False
            print(
                "Egress: ",
                group['GroupId'],
                group['GroupName'],
                protocol,
                fromport,
                toport,
                group['VpcId'],
                rule['CidrIp'],
            )

    # Empty groups - No ingress or egress rules
    if empty:
        print(
            "Group: ",
            group['GroupId'],
            group['GroupName'],
            group['VpcId'],
        )
