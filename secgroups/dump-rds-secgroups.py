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
rds = boto3.client('rds', region_name=region)
ec2 = boto3.client('ec2', region_name=region)


def main():

    # Get the account ID
    account_id = get_account_number()

    # group_paginator = ec2.get_paginator('describe_security_groups')
    # group_iterator = group_paginator.paginate()
    #
    # for page in group_iterator:
    #     for g in page['SecurityGroups']:

    instance_paginator = rds.get_paginator('describe_db_instances')
    instance_iterator = instance_paginator.paginate()

    for page in instance_iterator:
        for instance in page['DBInstances']:

            (name, bu, bs, ts) = get_identifying_tags(instance['TagList'])

            for instancesecuritygroup in instance['VpcSecurityGroups']:

                try:
                    securitygroups = ec2.describe_security_groups(
                        GroupIds=[instancesecuritygroup['VpcSecurityGroupId']]
                    )
                except ClientError as e:
                    print(e)

                # Ingress rules
                for group in securitygroups['SecurityGroups']:

                    for ippermission in group['IpPermissions']:

                        protocol = ippermission['IpProtocol']

                        if 'FromPort' in ippermission.keys():
                            fromport = str(ippermission['FromPort'])
                        else:
                            fromport = 'none'

                        if 'ToPort' in ippermission.keys():
                            toport = str(ippermission['ToPort'])
                        else:
                            toport = 'none'

                        if ippermission['IpProtocol'] == "-1":
                            protocol = 'all'
                            fromport = '0'
                            toport = "65535"


                        for rule in ippermission['UserIdGroupPairs']:

                            print(
                                account_id + ","
                                + name + ',' + bu + ',' + bs + ',' + ts + ','
                                + instance['DBInstanceIdentifier'] + ','
                                + instance['Endpoint']['Address'] + ','
                                + instance['DBSubnetGroup']['VpcId'] + ','
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
                                + instance['DBInstanceIdentifier'] + ','
                                + instance['Endpoint']['Address'] + ','
                                + instance['DBSubnetGroup']['VpcId'] + ','
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

                        protocol = ippermission['IpProtocol']

                        if 'FromPort' in ippermission.keys():
                            fromport = str(ippermission['FromPort'])
                        else:
                            fromport = 'none'

                        if 'ToPort' in ippermission.keys():
                            toport = str(ippermission['ToPort'])
                        else:
                            toport = 'none'

                        if ippermission['IpProtocol'] == "-1":
                            protocol = 'all'
                            fromport = '0'
                            toport = "65535"

                        for rule in ippermission['UserIdGroupPairs']:
                            print(
                                account_id + ","
                                + name + ',' + bu + ',' + bs + ',' + ts + ','
                                + instance['DBInstanceIdentifier'] + ','
                                + instance['Endpoint']['Address'] + ','
                                + instance['DBSubnetGroup']['VpcId'] + ','
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
                                + instance['DBInstanceIdentifier'] + ','
                                + instance['Endpoint']['Address'] + ','
                                + instance['DBSubnetGroup']['VpcId'] + ','
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

    if tags is None:
        name = "NONE"
        bu = "NONE"
        bs = "NONE"
        ts = "NONE"

    if len(tags) == 0:
        name = "NONE"
        bu = "NONE"
        bs = "NONE"
        ts = "NONE"
    else:
        tags = flatten_tags(tags)

        if 'BusinessUnit' in tags.keys():
            bu = tags['BusinessUnit']
        else:
            bu = "NONE"

        if 'BusinessService' in tags.keys():
            bs = tags['BusinessService']
        else:
            bs = "NONE"

        if 'TechnicalService' in tags.keys():
            ts = tags['TechnicalService']
        else:
            ts = "NONE"

        if 'Name' in tags.keys():
            name = tags['Name']
        else:
            name = "NONE"

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
