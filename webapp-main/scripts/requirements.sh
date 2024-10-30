#!/bin/bash

cd /home/csye6225/webapp-main || exit
ls -al
python3.12 -m venv venv
source venv/bin/activate
python3.12 -m pip install -r requirements.txt
sudo chmod -R +x /home/csye6225/webapp-main/venv
cd -
 
