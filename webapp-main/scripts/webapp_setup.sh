#!/bin/bash

sudo cp /tmp/webapp.service /etc/systemd/system/webapp.service

sudo ln -s /home/csye6225/webapp-main/app_log.log /var/log/app_log.log

sudo cp /tmp/appconfig.yaml /etc/google-cloud-ops-agent/config.yaml

 
sudo sed -i 's/^SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
sudo sed -i 's/^SELINUX=permissive/SELINUX=disabled/g' /etc/selinux/config
sudo setenforce 0
 
sudo systemctl daemon-reload
# sudo systemctl start webapp.service
sudo systemctl enable webapp.service
# sudo systemctl status webapp.service 
sudo systemctl restart google-cloud-ops-agent

 