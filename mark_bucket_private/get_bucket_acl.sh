#!/bin/bash

bucket=$1

aws s3api get-bucket-acl \
  --bucket $bucket

