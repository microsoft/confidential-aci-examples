#!/bin/bash

# Install Linux dependencies
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y cryptsetup

# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install python dependencies
pip install -r requirements.txt

# Install the policy generation tool
az extension add --name confcom

# Allow failure in the rest of setup as it relies on credentials which may not exist
set +e

# Setup the SSH_KEY
mkdir -p ~/.ssh
echo "$SSH_KEY" > ~/.ssh/id_rsa
chmod 600 ~/.ssh/id_rsa
ssh-keygen -y -f ~/.ssh/id_rsa > ~/.ssh/id_rsa.pub

# Import Keys
echo -e "$ENCRYPTION_KEY" | gpg --import
echo -e "$DECRYPTION_KEY" | gpg --import