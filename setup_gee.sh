#!/bin/bash
conda install pyCrypto google-cloud-sdk google-api-python-client -c conda-forge -y
conda install earthengine-api -c conda-forge -y
echo "When the web browser opens up, log in and allow google engine to do it's thing"
earthengine authenticate

