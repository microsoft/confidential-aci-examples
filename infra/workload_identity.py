# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
from io import BufferedWriter
import subprocess
import time 

CLUSTER_NAME = os.environ['CLUSTER_NAME']
RESOURCE_GROUP = os.environ['RESOURCE_GROUP']
LOCATION = os.environ['LOCATION']
SERVICE_ACCOUNT_NAMESPACE = os.environ['SERVICE_ACCOUNT_NAMESPACE'] 
SERVICE_ACCOUNT_NAME = os.environ['SERVICE_ACCOUNT_NAME']  

USER_ASSIGNED_IDENTITY_NAME = os.environ['USER_ASSIGNED_IDENTITY_NAME']
FEDERATED_IDENTITY_CREDENTIAL_NAME = os.environ['FEDERATED_IDENTITY_CREDENTIAL_NAME']

def enable_workload_identity_on_cluster():
    print ("checking workload identity enablement on cluster")
    workload_identity_enabled = run_command(" ".join(["az", "aks", "show", "--name", CLUSTER_NAME, "--resource-group", RESOURCE_GROUP, "--query 'securityProfile|workloadIdentity|enabled'" , "-otsv"]))
    print ("checking oidc issuer enablement on cluster")
    oidc_issuer_enabled = run_command(" ".join(["az", "aks", "show", "--name", CLUSTER_NAME, "--resource-group", RESOURCE_GROUP, "--query 'oidcIssuerProfile|enabled'" , "-otsv"]))
   
    if workload_identity_enabled != "true" or oidc_issuer_enabled != "true":
        res = run_command(" ".join(["az", "aks", "update", "--name", CLUSTER_NAME, "--resource-group", RESOURCE_GROUP, "--enable-workload-identity" , "--enable-oidc-issuer"]), terminate_on_command_fail=True)
        print (res) 
    else:
        print ("Workload identity is properly enabled on the cluster")
    

def setup_federated_identity(): 
    subscription = run_command(" ".join(["az", "account", "show", "--query", "id", "--output", "tsv"]))
    print(f"Setting SUBSCRIPTION to {subscription}")
    aks_oidc_issuer = run_command(" ".join(["az", "aks", "show", "--name", CLUSTER_NAME, "--resource-group", RESOURCE_GROUP, "--query", "oidcIssuerProfile.issuerUrl", "-otsv"]))
    print(f"Setting AKS_OIDC_ISSUER to {aks_oidc_issuer}")

    identity = run_command(" ".join(["az", "identity", "show", "--name", USER_ASSIGNED_IDENTITY_NAME, "--resource-group", RESOURCE_GROUP, "--subscription", subscription]))
    if "not found" in identity:
        print(f"Identity {USER_ASSIGNED_IDENTITY_NAME} not found. Creating...")
        run_command(" ".join(["az", "identity", "create", "--name", USER_ASSIGNED_IDENTITY_NAME, "--resource-group", RESOURCE_GROUP, "--location", LOCATION, "--subscription", subscription]))
    else:
        print(f"Identity {USER_ASSIGNED_IDENTITY_NAME} already exists.")

    user_assigned_client_id = run_command(" ".join(["az", "identity", "show", "--resource-group", RESOURCE_GROUP, "--name", USER_ASSIGNED_IDENTITY_NAME, "--query", "clientId", "-otsv"]))
    print(f"Setting USER_ASSIGNED_CLIENT_ID to {user_assigned_client_id}")

    managed_identity = run_command(" ".join(["az", "identity", "show", "--resource-group", RESOURCE_GROUP, "--name", USER_ASSIGNED_IDENTITY_NAME, "--query", "id", "-otsv"]))
    print(f"Setting MANAGED_IDENTITY to {managed_identity}")

    # Check kafka namespace existence and create if not found
    result = run_command(" ".join(["kubectl", "get", "namespace", "kafka"]))
    if "not found" in result:
        print ("kafka namespace not found. Create kafka namespace...")
        result = run_command(" ".join(["kubectl", "create", "namespace", "kafka"]), terminate_on_command_fail=True)
        print (result)
    else:
        print("kafka namespace already exists.")

    # Delete service account if it exists
    result = run_command(" ".join(["kubectl", "delete", "sa", "-n", "kafka", "workload-identity-sa"]))
    print (result)
    time.sleep(5)
    
    # Apply Kubernetes manifest for ServiceAccount
    os.environ['user_assigned_client_id'] = user_assigned_client_id
    os.environ['SERVICE_ACCOUNT_NAME'] = SERVICE_ACCOUNT_NAME
    os.environ['SERVICE_ACCOUNT_NAMESPACE'] = SERVICE_ACCOUNT_NAMESPACE
    result = run_command("rm workload_identity_sa.yaml")
    print (result)
    result = run_command("envsubst <../examples/e2e_kafka_encryption_demo/workload_identity_sa_template.yaml> workload_identity_sa.yaml")
    print (result)
    result = run_command("kubectl apply -f workload_identity_sa.yaml")
    print (result)


    # Check federated credential existence and create if not found
    result = run_command(" ".join(["az", "identity", "federated-credential", "show", "--name", FEDERATED_IDENTITY_CREDENTIAL_NAME, "--identity-name", USER_ASSIGNED_IDENTITY_NAME, "--resource-group", RESOURCE_GROUP]))
    if aks_oidc_issuer in result:
        print("Federated identity already exists.")
    else:
        print("Federated identity not found. Creating...")
        result = run_command(" ".join( ["az", "identity", "federated-credential", "create", "--name", FEDERATED_IDENTITY_CREDENTIAL_NAME, "--identity-name", USER_ASSIGNED_IDENTITY_NAME, "--resource-group", RESOURCE_GROUP, "--issuer", aks_oidc_issuer, "--subject", f"system:serviceaccount:{SERVICE_ACCOUNT_NAMESPACE}:{SERVICE_ACCOUNT_NAME}"]))


def install_aks_preview():
    aks_preview_existence = run_command("az extension list -o table | grep aks-preview")
    if aks_preview_existence:
        print ("az extension ask-preview already exists. Updating...")
        result = run_command("az extension update --name aks-preview")
        print (result)
    else: 
        print ("az extension ask-preview does not exist. Installing...")
        result = run_command("az extension add --name aks-preview")
        print (result)
        
    confcom_existence = run_command("az extension list -o  table | grep confcom")
    if confcom_existence:
        print ("az extension confcom already exists. Updating...")
        result = run_command("az extension update --name confcom")
        print (result)
    else: 
        print ("az extension confcom does not exist. Installing...")
        result = run_command("az extension add --name confcom")
        print (result)
    
    result = run_command("envsubst version")
    print (result)
    if "not found" in result: 
        print ("envsubst binary not found in path, install...")
        result = subprocess.check_call("sudo curl -L https://github.com/a8m/envsubst/releases/download/v1.2.0/envsubst-`uname -s`-`uname -m` -o envsubst", shell=True)
        result = subprocess.check_call("chmod +x envsubst", shell=True)
        result = subprocess.check_call("sudo mv envsubst /usr/local/bin", shell=True)
    
    release_string = "curl -LO \"https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl\""
    result = run_command(release_string)
    result = subprocess.check_call("chmod +x kubectl", shell=True)
    result = subprocess.check_call("sudo mv kubectl /usr/local/bin", shell=True)

    result = run_command("az feature register --namespace Microsoft.ContainerService --name KataCcIsolationPreview", terminate_on_command_fail=True)
    print (result)
    time.sleep(5)
    result = run_command("az feature show --namespace Microsoft.ContainerService --name KataCcIsolationPreview", terminate_on_command_fail=True)
    print (result)
    time.sleep(5)
    # Register provider
    result = run_command("az provider register --namespace Microsoft.ContainerService", terminate_on_command_fail=True)
    print (result)
    time.sleep(5)
    
    
def create_cluster(): 
    # Create AKS cluster
    aks_create_command = [
        "az", "aks", "create",
        "--resource-group", "c-aci-examples",
        "--name", "skr-kafka-demo-rg-testing12n7",
        "--kubernetes-version", "1.28.3",
        "--os-sku", "AzureLinux",
        "--node-vm-size", "Standard_DC4as_cc_v5",
        "--enable-oidc-issuer",
        "--enable-workload-identity",
        "--workload-runtime", "KataCcIsolation",
        "--node-count", "1",
        "--generate-ssh-keys"
    ]
    result = run_command(" ".join(aks_create_command), terminate_on_command_fail=True)
    print (result )

    # Get AKS credentials
    aks_get_credentials_command = [
        "az", "aks", "get-credentials",
        "--resource-group", "c-aci-examples",
        "--name", "skr-kafka-demo-rg-testing12n7",
        "--overwrite-existing"
    ]
    result = run_command(" ".join(aks_get_credentials_command), terminate_on_command_fail=True)
    print (result)
    
   
def run_command(cmd, terminate_on_command_fail=False):
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output = result.stdout.strip()
    if result.returncode != 0:
        output = result.stderr.strip()
        if terminate_on_command_fail:
            print (output)
            exit(1) 
        return output
    return output