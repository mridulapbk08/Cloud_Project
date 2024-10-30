#!/bin/bash
sudo dnf install unzip -y
sudo mkdir -p /home/csye6225/webapp-main/
sudo unzip /tmp/webapp-main.zip -d /home/csye6225/webapp-main/
sudo chown -R csye6225:csye6225 /home/csye6225/webapp-main