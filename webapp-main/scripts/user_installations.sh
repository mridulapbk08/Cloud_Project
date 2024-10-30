#!/bin/bash

# Create User
sudo groupadd csye6225
sudo useradd -m -g csye6225 -s /usr/sbin/nologin csye6225


#install python
sudo dnf install python3.12 -y
sudo dnf -y groupinstall development 

curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
sudo bash add-google-cloud-ops-agent-repo.sh --also-install