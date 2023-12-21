# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import json
import os
import subprocess
import time

from infra.workload_identity import install_aks_preview, create_cluster, tests
from infra.resolve_manifest_variables import resolve_manifest_variables
from infra.deploy_arm_template import run_pre_deploy_script


def setUpAks(cls):
    if "UNIQUE_ID" not in os.environ:
        os.environ["UNIQUE_ID"] = cls.name
    cls.manifest = resolve_manifest_variables(cls.manifest)

    tests()
    # install_aks_preview()
    # create_cluster()

    if "preDeployScript" in cls.manifest:
        run_pre_deploy_script(cls.manifest, "")

def tearDownAks(cls):
    pass
    # res = subprocess.run("kubectl delete -f consumer-example.yaml", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    # if res.returncode != 0:
    #     print ("'kubectl delete -f consumer-example.yaml' command failed. Error messgae: ")
    #     print (res.stderr)
    # else: 
    #     print ("Delete consumer succeeded")
    #     print (res.stdout)
    
    # res = subprocess.run("kubectl delete -f producer-example.yaml", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    # if res.returncode != 0:
    #     print ("'kubectl delete -f producer-example.yaml' command failed. Error messgae: ")
    #     print (res.stderr)
    # else: 
    #     print ("Delete producer succeeded")
    #     print (res.stdout)
        
    # res = subprocess.run("kubectl -n kafka delete $(kubectl get strimzi -o name -n kafka)", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    # if res.returncode != 0:
    #     print ("'kubectl -n kafka delete $(kubectl get strimzi -o name -n kafka)' command failed. Error messgae: ")
    #     print (res.stderr)
    # else: 
    #     print ("Delete strimzi succeeded")
    #     print (res.stdout)
        
    # res = subprocess.run("kubectl -n kafka delete -f 'https://strimzi.io/install/latest?namespace=kafka'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    # if res.returncode != 0:
    #     print ("kubectl -n kafka delete -f 'https://strimzi.io/install/latest?namespace=kafka' command failed. Error messgae: ")
    #     print (res.stderr)
    # else: 
    #     print ("Delete kafka cluster succeeded")
    #     print (res.stdout)
        
    # res = subprocess.run("kubectl delete namespace kafka", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    # if res.returncode != 0:
    #     print ("kubectl -n kafka delete -f 'https://strimzi.io/install/latest?namespace=kafka' command failed. Error messgae: ")
    #     print (res.stderr)
    # else: 
    #     print ("Delete kafka namespace succeeded")
    #     print (res.stdout)
        
    # res = subprocess.run("az aks stop --resource-group accct-mariner-kata-aks-testing --name skr-kafka-demo-rg-7625", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    # if res.returncode != 0:
    #     print ("az aks stop --resource-group accct-mariner-kata-aks-testing --name skr-kafka-demo-rg-7625' command failed. Error messgae: ")
    #     print (res.stderr)
    # else: 
    #     print ("Stopping AKS cluster succeeded")
    #     print (res.stdout)

    # res = subprocess.run("az aks delete --resource-group accct-mariner-kata-aks-testing --name skr-kafka-demo-rg-7625 --no-wait", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    # if res.returncode != 0:
    #     print ("async az aks delete cluster command failed. Error messgae: ")
    #     print (res.stderr)
    # else: 
    #     print ("Delete AKS cluster succeeded")
    #     print (res.stdout)

