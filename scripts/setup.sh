#!/bin/bash

# This is a script to quickly set up Travis CI for any repo. It assumes a few
# things:
# 1) You have jq, travis CLI, git, AWS command line installed
# 2) You store a secret with some configuration in AWS Secrets Manager
# This script will automatically give you Git repo tags, linting, tests,
# and published docker images to a private repository!

# This configuration should look like this:
# {
#   "GIT_ORG": "your-github-org",
#   "GIT_TOKEN": "your-github-https-token",
#   "SLACK_SPACE": "your-slack-space",
#   "SLACK_TOKEN": "your-slack-token",
#   "AWS_ACCESS_KEY_ID": "access key ID",
#   "AWS_SECRET_ACCESS_KEY": "secret access key",
#   "AWS_REGION": "AWS Region",
# }

set -e

# Set up config
echo "Fetching config..."
CONFIG_NAME=dev_config
CONFIG=$(aws secretsmanager get-secret-value \
  --secret-id $CONFIG_NAME \
  --query SecretString \
  --output text)

echo "Parsing config..."
# Inferred variables
GIT_REPO=$(basename `git rev-parse --show-toplevel`)

# Variables fetched from config
GIT_ORG=$(echo $CONFIG | jq .GIT_ORG -r)
GIT_TOKEN=$(echo $CONFIG | jq .GIT_TOKEN -r)
SLACK_SPACE=$(echo $CONFIG | jq .SLACK_SPACE -r)
SLACK_TOKEN=$(echo $CONFIG | jq .SLACK_TOKEN -r)
AWS_ACCESS_KEY_ID=$(echo $CONFIG | jq .AWS_ACCESS_KEY_ID -r)
AWS_SECRET_ACCESS_KEY=$(echo $CONFIG | jq .AWS_SECRET_ACCESS_KEY -r)
AWS_REGION=$(echo $CONFIG | jq .AWS_REGION -r)

echo "Applying config..."
# Travis set up
travis login --github-token $GIT_TOKEN --com --no-interactive
travis encrypt "$SLACK_SPACE:$SLACK_TOKEN" --add notifications.slack --com --no-interactive
travis env set GIT_ORG $GIT_ORG --no-interactive
travis env set GIT_TOKEN $GIT_TOKEN --no-interactive
travis env set GIT_REPO $GIT_REPO --no-interactive
travis env set AWS_ACCESS_KEY_ID $AWS_ACCESS_KEY_ID --no-interactive
travis env set AWS_SECRET_ACCESS_KEY $AWS_SECRET_ACCESS_KEY --no-interactive
travis env set AWS_REGION $AWS_REGION --no-interactive

echo "Done!"
