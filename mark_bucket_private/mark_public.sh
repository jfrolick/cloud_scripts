#!/bin/bash

bucket=$1

printf "$bucket\n"

aws s3api put-public-access-block \
  --bucket $bucket \
  --public-access-block-configuration '{ "BlockPublicAcls": false, "IgnorePublicAcls": false, "BlockPublicPolicy": false, "RestrictPublicBuckets": false }'

aws s3api get-public-access-block \
--bucket $bucket
