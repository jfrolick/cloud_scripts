#!/usr/bin/env python3

import json
import boto3
import sys
import re
import ipdb
import argparse
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


# Get the account ID

def get_account_number():

    _client = boto3.client("sts")

    account_id = _client.get_caller_identity()["Account"]

    return account_id


account_id = get_account_number()

# Loop through groups

for group in secgroups['SecurityGroups']:

    empty = True

    # Ingress rules
    for ippermission in group['IpPermissions']:

        if ippermission['IpProtocol'] == "tcp":
            protocol = ippermission['IpProtocol']
            fromport = str(ippermission['FromPort'])
            toport = str(ippermission['ToPort'])
        elif ippermission['IpProtocol'] == "udp":
            protocol = ippermission['IpProtocol']
            fromport = str(ippermission['FromPort'])
            toport = str(ippermission['ToPort'])
        elif ippermission['IpProtocol'] == "-1":
            protocol = "all"
            fromport = "0"
            toport = "65535"
        else:
            protocol = "unknown"
            fromport = "unknown"
            toport = "unknown"

        for rule in ippermission['UserIdGroupPairs']:
            empty = False
            print(
                "AccountId:" +  account_id + ", " +
                "Ingress:(" +
                "GroupId:" +  group['GroupId'] + ",",
                "GroupName:\"" +  group['GroupName'] + "\",",
                "GroupVpcId:" +  group['VpcId'] + ",",
                "Protocol:" +  protocol + ",",
                "Ports:" +  fromport + "-" +  toport + ",",
                "IngressGroup:" +  rule['GroupId'] + ",",
                "IngressAccount:" +  rule['UserId'] +
                ")"
            )

            # Find group VPC
            groupvpc = list(
                filter(
                    lambda x: x['GroupId'] == rule['GroupId'],
                    secgroups['SecurityGroups']
                )
            )

            if len(groupvpc) > 0:
                if group['VpcId'] != groupvpc[0]['VpcId']:
                    print(
                        "AccountId:" +  account_id + ", " +
                        "Warning:\"(TGW) Security group VpcId does not match ingress rule security group VPC ID\",",
                        "GroupId:" +  group['GroupId'] + ",",
                        "GroupVpcId:" +  group['VpcId'] + ",",
                        "IngressVpcId:" +  groupvpc[0]['VpcId']
                    )
            else:
                print ("Ingress rule group ID does not exist - " +  rule['GroupId'])

        for rule in ippermission['IpRanges']:
            empty = False
            print(
                "AccountId:" +  account_id + ", " +
                "Ingress:(" +
                "GroupId:" +  group['GroupId'] + ",",
                "GroupName:\"" +  group['GroupName'] + "\",",
                "GroupVpcId:" +  group['VpcId'] + ",",
                "Protocol:" +  protocol + ",",
                "Ports:" +  fromport + "-" +  toport + ",",
                "CIDR:" +  rule['CidrIp'] + ")"
            )


    # Egress rules

    for ippermission in group['IpPermissionsEgress']:


        if ippermission['IpProtocol'] == "tcp":
            protocol = ippermission['IpProtocol']
            fromport = str(ippermission['FromPort'])
            toport = str(ippermission['ToPort'])
        elif ippermission['IpProtocol'] == "udp":
            protocol = ippermission['IpProtocol']
            fromport = str(ippermission['FromPort'])
            toport = str(ippermission['ToPort'])
        elif ippermission['IpProtocol'] == "-1":
            protocol = "all"
            fromport = "0"
            toport = "65535"
        else:
            protocol = "unknown"
            fromport = "unknown"
            toport = "unknown"

        for rule in ippermission['UserIdGroupPairs']:
            empty = False
            print(
                "AccountId:" +  account_id + ", " +
                "Egress:(" +
                "GroupId:" +  group['GroupId'] + ",",
                "GroupName:\"" +  group['GroupName'] + "\",",
                "GroupVpcId:" +  group['VpcId'] + ",",
                "Protocol:" +  protocol + ",",
                "Ports:" +  fromport + "-" +  toport + ",",
                "EgressGroup:" +  rule['GroupId'] + ",",
                "EgressAccount:" +  rule['UserId'] +
                ")"
            )

            # Find group VPC
            groupvpc = list(
                filter(
                    lambda x: x['GroupId'] == rule['GroupId'],
                    secgroups['SecurityGroups']
                )
            )

            if len(groupvpc) > 0:
                if group['VpcId'] != groupvpc[0]['VpcId']:
                    print(
                        "AccountId:" +  account_id + ", " +
                        "Warning:\"(TGW) Security group VpcId does not match egress rule security group VPC ID\",",
                        "GroupId:" +  group['GroupId'] + ",",
                        "GroupVpcId:" +  group['VpcId'] + ",",
                        "EgressVpcId:" +  groupvpc[0]['VpcId']
                    )
            else:
                print ("Egress rule group ID does not exist - " +  rule['GroupId'])

        for rule in ippermission['IpRanges']:
            empty = False
            print(
                "AccountId:" +  account_id + ", " +
                "Egress:(" +
                "GroupId:" +  group['GroupId'] + ",",
                "GroupName:\"" +  group['GroupName'] + "\",",
                "GroupVpcId:" +  group['VpcId'] + ",",
                "Protocol:" +  protocol + ",",
                "Ports:" +  fromport + "-" +  toport + ",",
                "CIDR:" +  rule['CidrIp'] + ")"
            )

    # Empty groups - No ingress or egress rules
    if empty:
        print(
            "AccountId:" +  account_id + ", " +
            "GroupId:" +  group['GroupId'],
            "GroupName:\"" +  group['GroupName'] + "\"",
            "GroupVpcId:" +  group['VpcId'],
        )
