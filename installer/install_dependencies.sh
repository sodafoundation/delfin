#!/bin/bash

echo Enabling docker repository
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg --yes

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  
# Update local repositories
echo Updating local repositories
sudo apt-get update

# Install dependencies
echo Installing dependencies
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg gnupg-agent lsb-release software-properties-common sshpass pv gawk

# Install python dependencies
echo Installing Python dependencies
sudo apt-get install -y python3-distutils
sudo apt-get install -y python3-pip

# Install ansible if not present
if [ "`which ansible`" != ""  ]; then
    echo ansible already installed, skipping.
else
    echo Installing ansible
    python3 -m pip install --user ansible
fi

# Install docker if not present
if [ "`which docker`" != ""  ]; then
    echo Docker already installed, skipping.
else
    echo Installing docker
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
fi

# Ensure /usr/local/bin is in path
export PATH=$PATH:/usr/local/bin
