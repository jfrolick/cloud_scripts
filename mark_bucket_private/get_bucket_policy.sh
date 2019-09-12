#!/bin/bash

bucket=$1

aws s3api get-bucket-policy \
  --bucket $bucket \
  | jq -r '.Policy' \
  | jq .
