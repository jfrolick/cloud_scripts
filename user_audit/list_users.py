#!/usr/bin/env python

import json
import boto3
import sys
import re
import ipdb
import datetime
import dateutil

from datetime import datetime
from dateutil.tz import tzutc
from dateutil import parser

iam = boto3.client('iam')

users = iam.list_users()

for i in users['Users']:

    groups = iam.list_groups_for_user(UserName=i['UserName'])
    policies = iam.list_user_policies(UserName=i['UserName'])
    mfadevices = iam.list_mfa_devices(UserName=i['UserName'])
    accesskeys = iam.list_access_keys(UserName=i['UserName'])

    if 'PasswordLastUsed' in i.keys():
        passwordLastUsed = datetime.now(i['PasswordLastUsed'].tzinfo)
    else:
        passwordLastUsed = "NONE"

    if groups is None:
        groups = "NO GROUPS"

    if policies is None:
        policies = "NO POLICIES"

    if mfadevices is None:
        mfadevices = "NO MFA DEVICES"

    if accesskeys is None:
        accesskeys = "NO KEYS"

    print i['UserName'], ': \n' \
        '  PasswordLastUsed: ', passwordLastUsed, '\n' \
        '  CreateDate: ', i['CreateDate'], '\n' \
        '  UserId: ', i['UserId'], '\n' \
        '  ARN: ', i['Arn'], "\n", \
        '  Groups: ', groups, "\n", \
        '  Policies: ', policies, "\n", \
        '  MFA Devices: ', mfadevices, '\n', \
        '  Access Keys: ', accesskeys, '\n'

# paginator = iam.get_paginator('list_users')
#
# for response in paginator.paginate():
#     for i in response:
#         print(i)
