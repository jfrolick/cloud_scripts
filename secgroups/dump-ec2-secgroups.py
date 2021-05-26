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


def main():

    # Get the account ID
    account_id = get_account_number()

    # group_paginator = ec2.get_paginator('describe_security_groups')
    # group_iterator = group_paginator.paginate()
    #
    # for page in group_iterator:
    #     for g in page['SecurityGroups']:


    instance_paginator = ec2.get_paginator('describe_instances')
    instance_iterator = instance_paginator.paginate()

    for page in instance_iterator:
        for reservation in page['Reservations']:
            for instance in reservation['Instances']:

                (name, bu, bs, ts) = get_identifying_tags(instance['Tags'])

                for instancesecuritygroup in instance['SecurityGroups']:

                    try:
                        securitygroups = ec2.describe_security_groups(
                            GroupIds=[instancesecuritygroup['GroupId']]
                        )
                    except ClientError as e:
                        print(e)

                    # Ingress rules
                    for group in securitygroups['SecurityGroups']:
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

                                print(
                                    account_id + ","
                                    + name + ',' + bu + ',' + bs + ',' + ts + ','
                                    + instance['InstanceId'] + ','
                                    + instance['PrivateIpAddress'] + ','
                                    + instance['VpcId'] + ','
                                    + group['GroupId'] + ","
                                    + group['GroupName'] + ","
                                    + "Ingress,"
                                    + group['VpcId'] + ","
                                    + protocol + ","
                                    + fromport + "-" +  toport + ","
                                    + rule['GroupId'] + "/"
                                    + rule['UserId']
                                )

                            for rule in ippermission['IpRanges']:
                                print(
                                    account_id + ","
                                    + name + ',' + bu + ',' + bs + ',' + ts + ','
                                    + instance['InstanceId'] + ','
                                    + instance['PrivateIpAddress'] + ','
                                    + instance['VpcId'] + ','
                                    + group['GroupId'] + ","
                                    + group['GroupName'] + ","
                                    + "Ingress,"
                                    + group['VpcId'] + ","
                                    + protocol + ","
                                    + fromport + "-" +  toport + ","
                                    + rule['CidrIp']
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
                                print(
                                    account_id + ","
                                    + name + ',' + bu + ',' + bs + ',' + ts + ','
                                    + instance['InstanceId'] + ','
                                    + instance['PrivateIpAddress'] + ','
                                    + instance['VpcId'] + ','
                                    + group['GroupId'] + ","
                                    + group['GroupName'] + ","
                                    + "Egress,"
                                    + group['VpcId'] + ","
                                    + protocol + ","
                                    + fromport + "-" +  toport + ","
                                    + rule['GroupId'] + "/"
                                    + rule['UserId']
                                )

                            for rule in ippermission['IpRanges']:
                                print(
                                    account_id + ","
                                    + name + ',' + bu + ',' + bs + ',' + ts + ','
                                    + instance['InstanceId'] + ','
                                    + instance['PrivateIpAddress'] + ','
                                    + instance['VpcId'] + ','
                                    + group['GroupId'] + ","
                                    + group['GroupName'] + ","
                                    + "Egress,"
                                    + group['VpcId'] + ","
                                    + protocol + ","
                                    + fromport + "-" +  toport + ","
                                    + rule['CidrIp'] + ")"
                                )


def process_rules(rules):
    return ""

def get_identifying_tags(tags):

    tags = flatten_tags(tags)

    if 'BusinessUnit' in tags.keys():
        bu = tags['BusinessUnit']
    else:
        bu = "NONE"

    if 'BusinessService' in tags.keys():
        bs = tags['BusinessService']
    else:
        bu = "NONE"

    if 'TechnicalService' in tags.keys():
        ts = tags['TechnicalService']
    else:
        bu = "NONE"

    if 'Name' in tags.keys():
        name = tags['Name']
    else:
        bu = "NONE"

    return name, bu, bs, ts

def get_account_number():

    _client = boto3.client("sts")

    account_id = _client.get_caller_identity()["Account"]

    return account_id


# Flatten array of hashes to hash of hashes
def flatten_tags(tags):

    flattened = {}

    if len(tags) < 1:
        return None

    for i in tags:
        flattened[i['Key']] = i['Value']

    return flattened

main()
