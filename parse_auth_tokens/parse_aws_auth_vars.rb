#!/usr/bin/env ruby

require 'json'
require 'timeout'

hopefully_json = ""

begin
  Timeout.timeout(10) do
    hopefully_json = STDIN.read
  end
rescue Timeout::Error => e
#  puts "Timed out waiting for input.\n"
  exit 1
end

def valid_json?(string)
  begin
    !!JSON.parse(string)
  rescue JSON::ParserError
    false
  end
end

exit 2 if ! valid_json?(hopefully_json)

doc = JSON.parse(hopefully_json)

if doc.has_key?("AssumedRoleUser")
  puts "export AWS_ASSUMED_ROLE=\"" + doc["AssumedRoleUser"]["AssumedRoleId"] + "\""
end
if doc.has_key?("Credentials")
  puts "export AWS_ACCESS_KEY_ID=\"" + doc["Credentials"]["AccessKeyId"] + "\""
  puts "export AWS_SECRET_ACCESS_KEY=\"" + doc["Credentials"]["SecretAccessKey"] + "\""
  puts "export AWS_SESSION_TOKEN=\"" + doc["Credentials"]["SessionToken"] + "\""
else
  exit 3
end
