# Setup the SSH_KEY
mkdir ~/.ssh
echo "$SSH_KEY" > ~/.ssh/id_rsa
chmod 600 ~/.ssh/id_rsa
ssh-keygen -y -f ~/.ssh/id_rsa > ~/.ssh/id_rsa.pub

# Install python dependencies
pip install -r requirements.txt

# Install the policy generation tool
az extension add --name confcom

# Allow failure in the rest of setup as it relies on credentials which may not exist
set +e

# Login into Azure CLI
az login --service-principal \
    --username $AZURE_SERVICE_PRINCIPAL_APP_ID \
    --password $AZURE_SERVICE_PRINCIPAL_PASSWORD \
    --tenant $AZURE_SERVICE_PRINCIPAL_TENANT

# Login into Container Registry
az acr login --name $AZURE_REGISTRY_URL

# Import Keys
echo -e "$ENCRYPTION_KEY" | gpg --import
echo -e "$DECRYPTION_KEY" | gpg --import