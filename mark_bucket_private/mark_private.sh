#!/bin/bash

bucket=$1

printf "$bucket\n"

aws s3api put-public-access-block \
  --bucket $bucket \
  --public-access-block-configuration '{ "BlockPublicAcls": true, "IgnorePublicAcls": true, "BlockPublicPolicy": true, "RestrictPublicBuckets": true }'

aws s3api get-public-access-block \
--bucket $bucket
