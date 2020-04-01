#!/usr/bin/env python3

import json
import boto3
import sys
import re
import ipdb
import os
from botocore.exceptions import ClientError

region = os.getenv('AWS_DEFAULT_REGION')
ec2 = boto3.resource('ec2', region_name=region)

client = boto3.client('ec2')


# Get list of VPCs
vpcs = client.describe_vpcs()['Vpcs']


# Get list of route tables
route_tables = client.describe_route_tables()['RouteTables']


def get_account_number():

    _client = boto3.client("sts")

    account_id = _client.get_caller_identity()["Account"]

    return account_id


def flatten_tags(tags):

    flattened = {}

    if len(tags) < 1:
        return None

    for i in tags:
        flattened[i['Key']] = i['Value']

    return flattened


def get_vcp_name(vpc_id):

    for i in vpcs:
        if i['VpcId'] == vpc_id:
            tags = flatten_tags(i['Tags'])
            # print json.dumps(
            #     tags,
            #     sort_keys=True,
            #     indent=2,
            #     separators=(',', ': ')
            # )
            return tags['Name']

    return ""


def get_rt_name(rt):

    for i in route_tables:

        if i['RouteTableId'] == rt:

            if not isinstance(i['Tags'], list):
                return None

            if 'Tags' in i.keys():

                tags = flatten_tags(i['Tags'])

                if tags is None:
                    return None

                if 'Name' in tags.keys():
                    return tags['Name']

    return None


def get_route_tables(vpc_id):

    vpc_route_tables = []

    for i in route_tables:
        if i['VpcId'] == vpc_id:
            vpc_route_tables.append(i['RouteTableId'])

    return vpc_route_tables


def get_routes(rt):

    routes = []

    for i in route_tables:

        if i['RouteTableId'] == rt:

            for r in i['Routes']:
                routes.append(r)

            return routes

    return None


my_account = get_account_number()



for v in vpcs:
    tables = get_route_tables(v['VpcId'])
    for t in tables:
        routes = get_routes(t)
        for i, route in enumerate(routes):
            if 'VpcPeeringConnectionId' in route:
                if route['State'] == 'blackhole':
                    print (my_account, " ", region, " ", v['VpcId'], " ", t, " ", get_rt_name(t), " ", route['DestinationCidrBlock'], " ", route['State'], " ", route['VpcPeeringConnectionId'])
                    client.delete_route(
                        RouteTableId = t,
                        DestinationCidrBlock = route['DestinationCidrBlock']
                    )
