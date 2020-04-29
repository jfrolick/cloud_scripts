#!/usr/bin/env python

import json
import boto3
import sys
import re
import ipdb
import os
from botocore.exceptions import ClientError


route_table_filter = 'private'

region = os.getenv('AWS_DEFAULT_REGION')
ec2 = boto3.resource('ec2', region_name=region)

client = boto3.client('ec2')


# Get list of peering connections
peering_connections = \
    client.describe_vpc_peering_connections()['VpcPeeringConnections']

# Get list of VPCs
vpcs = client.describe_vpcs()['Vpcs']

# Get list of route tables
route_tables = client.describe_route_tables()['RouteTables']

# print json.dumps(
#     route_tables,
#     sort_keys=True,
#     indent=2,
#     separators=(',', ': ')
# )

#ipdb.set_trace()


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


def get_active_peering_connections():

    active_connections = []

    if len(peering_connections) < 1:
        return []

    for i, c in enumerate(peering_connections):

        if c['Status']['Code'] == "deleted":
            continue

#        if c['RequesterVpcInfo']['OwnerId'] == my_account:
#            continue

        active_connections.append(c)

    return active_connections


def get_cidr_blocks(vpc_id):

    cidr_blocks = []
    vpc = []

    for i in vpcs:
        if i['VpcId'] == vpc_id:
            vpc = i
            break
    else:
        return []

    # print json.dumps(vpcs, sort_keys=True, indent=2, separators=(',', ': '))

    if 'CidrBlockAssociationSet' in vpc.keys():
        for i in vpc['CidrBlockAssociationSet']:
            if i['CidrBlockState']['State'] == 'associated':
                cidr_blocks.append(i['CidrBlock'])

    if 'Ipv6CidrBlockAssociationSet' in vpc.keys():
        for i in vpc['Ipv6CidrBlockAssociationSet']:
            if i['Ipv6CidrBlockState']['State'] == 'associated':
                cidr_blocks.append(i['Ipv6CidrBlock'])

    return cidr_blocks


def get_vcp_name(vpc_id):

    for i in vpcs:

        if i['VpcId'] == vpc_id:

            if not isinstance(i['Tags'], list):
                return None

            if 'Tags' in i.keys():
                tags = flatten_tags(i['Tags'])

            tags = flatten_tags(i['Tags'])

            if tags is None:
                return None

            if 'Name' in tags.keys():
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


def add_routes(_route_tables, connection_id, cidr, filter):

    for route_table in _route_tables:

        if get_rt_name(route_table) is None:
            # print "Skipping untagged route table:", i
            continue

        m = re.search(filter, get_rt_name(route_table))

        if m:

            routes = get_routes(route_table)

            # print json.dumps(
            #     routes,
            #     sort_keys=True,
            #     indent=2,
            #     separators=(',', ': ')
            # )

            for i, route in enumerate(routes):
                if 'VpcPeeringConnectionId' in route:
                    if 'DestinationCidrBlock' in route:
                        if cidr == route['DestinationCidrBlock']:
                            print "\tRoute exists for cidr " + cidr + \
                                " in table " + route_table + \
                                " to destination " + connection_id
                            break
            else:
                print "\tAdding route for cidr " + cidr + \
                    " to table " + route_table + \
                    " with destination " + connection_id
                try:
                    client.create_route(
                        RouteTableId = route_table,
                        DestinationCidrBlock = cidr,
                        VpcPeeringConnectionId = connection_id
                    )
                except ClientError as e:
                    if e.response['Error']['Code'] == "RouteAlreadyExists":
                        print "Route exists."
                    else:
                        print(e)
                        sys.exit(1)


my_account = get_account_number()
connections = get_active_peering_connections()

if len(connections) < 1:
    sys.exit(0)

for i, c in enumerate(connections):

    # print json.dumps(c, sort_keys=True, indent=2, separators=(',', ': '))

    print "Connection ID:     ", c['VpcPeeringConnectionId'], "\n"
    print "Accepter Account:  ", c['AccepterVpcInfo']['OwnerId']
    print "Accepter VPCID:    ", c['AccepterVpcInfo']['VpcId']
    print "Accepter Region:   ", c['AccepterVpcInfo']['Region']
    print "Accepter CIDR:     ", c['AccepterVpcInfo']['CidrBlock']
    print "Accepter VPC Name: ", get_vcp_name(c['AccepterVpcInfo']['VpcId'])

    print "Accepter CIDR Blocks:"
    for i in get_cidr_blocks(c['AccepterVpcInfo']['VpcId']):
        print "\t" + i

    print "Accepter Route Tables:"
    for i in get_route_tables(c['AccepterVpcInfo']['VpcId']):
        print "\t" + i, get_rt_name(i)

    print "\nRequester Owner:  ", c['RequesterVpcInfo']['OwnerId']
    print "Requester VPCID:  ", c['RequesterVpcInfo']['VpcId']
    print "Requester Region: ", c['RequesterVpcInfo']['Region']
    print "Requester CIDR:   ", c['RequesterVpcInfo']['CidrBlock']

    if c['RequesterVpcInfo']['OwnerId'] == c['AccepterVpcInfo']['OwnerId']:

        print "\nRequester VPC Name",
        get_vcp_name(c['RequesterVpcInfo']['VpcId']), "\n"
        print "Requester CIDR Blocks:"
        print get_cidr_blocks(c['RequesterVpcInfo']['VpcId']), "\n"
        print "Requester Route Tables:"
        print get_route_tables(c['RequesterVpcInfo']['VpcId']), "\n"

    add_routes(
        get_route_tables(c['AccepterVpcInfo']['VpcId']),
        c['VpcPeeringConnectionId'],
        c['RequesterVpcInfo']['CidrBlock'],
        route_table_filter
    )

    print "\n"
