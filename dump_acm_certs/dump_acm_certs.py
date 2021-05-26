#!/usr/bin/env python3

import json
import boto3
import sys
import re
import ipdb
import argparse
import re
from botocore.exceptions import ClientError

parser = argparse.ArgumentParser(
    description='Query ACM and print information about certificates'
)

parser.add_argument(
    '--type',
    '-t',
    help = "Certificate type"
)

parser.add_argument(
    '--region',
    '-r',
    help = 'AWS Region'
)

parser.add_argument(
    '--verbose',
    '-v'
    help =
)

args = parser.parse_args()

if args.region:
    os.environ['DEFAULT_AWS_REGION'] = args.region

wildcard_re = re.compile('^\*\.', re.IGNORECASE)

client = boto3.client('acm')

certificate_paginator = client.get_paginator('list_certificates')
certificate_iterator = certificate_paginator.paginate()

for page in certificate_iterator:

    for i in page['CertificateSummaryList']:

        # print(i['CertificateArn'])
        certificate = client.describe_certificate(
            CertificateArn = i['CertificateArn']
        )

        if certificate['Certificate']['Type'] == 'IMPORTED':
            next

        for i in certificate['Certificate']['SubjectAlternativeNames']:
            m = wildcard_re.match(i)
            if m:
                wildcard = "TRUE"
            else:
                wildcard = "FALSE"

        if wildcard == 'TRUE':
            next

        if len(certificate['Certificate']['SubjectAlternativeNames']) > 1:

            print("./csrgen.py --name {} -s {} -u csrgen.yaml".format(
                certificate['Certificate']['DomainName'],
                ' '.join(certificate['Certificate']['SubjectAlternativeNames'])
                )
            )

        else:
            # print("Certificate:{}, Wildcard:{} Type:{}".format(
            #     certificate['Certificate']['DomainName'],
            #     wildcard,
            #     certificate['Certificate']['Type']
            #     )
            # )

            print("./csrgen.py --name {} -u csrgen.yaml".format(
                certificate['Certificate']['DomainName']
                )
            )
