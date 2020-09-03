#!/usr/bin/env bash

set -ex

sudo yum update -y
sudo yum install docker -y
sudo systemctl enable docker
sudo systemctl start docker
sudo chown -R ec2-user /var/run/
eval $(aws ecr get-login --no-include-email --region us-east-1)

docker run -p 443:5000 -d 111373087273.dkr.ecr.us-east-1.amazonaws.com/api.zacharyjklein.com:stable
