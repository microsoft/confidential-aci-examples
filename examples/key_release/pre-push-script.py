# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse
import json
import subprocess
import tempfile
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

def generate_rsa_key(name: str):
    print("Generating RSA key: ", name)

    hsm_name = os.environ['AZURE_HSM_ENDPOINT'].split('.managedhsm')[0]
    pub_key_file = f"{name}-pub.pem"
    key_info_file = f"{name}-info.json"
    
    # create release policy file for rsa key
    with tempfile.NamedTemporaryFile() as f, open(key_info_file, 'w') as key_info:
        f.write(bytes(json.dumps(
            {
                "version": "0.2",
                "anyOf": [
                    {
                        "authority": f"https://{os.environ['AZURE_ATTESTATION_ENDPOINT']}",
                        "allOf": [
                            {
                                "claim": "x-ms-attestation-type",
                                "equals": "sevsnpvm"
                            },
                        ],
                    }
                ],
            }
        ), encoding='utf8'))

        f.seek(0)

        # create rsa key in mHSM
        subprocess.check_call(f"az keyvault key create --id https://{os.environ['AZURE_HSM_ENDPOINT']}/keys/{name} --ops wrapKey unwrapkey encrypt decrypt --kty RSA-HSM --size 3072 --exportable --policy {f.name}", shell=True)
        # download public key
        subprocess.check_call(f"az keyvault key download --hsm-name {hsm_name} -n {name} -f {pub_key_file}", shell=True)

        # create key info file
        key_info.write(json.dumps(
            {
                "public_key_path": pub_key_file, 
                "kms_endpoint": os.environ['AZURE_HSM_ENDPOINT'], 
                "attester_endpoint": os.environ['AZURE_ATTESTATION_ENDPOINT']
            }
        ))

def generate_wrapped_data(key):
    # get skr executable
    subprocess.run("curl -L https://github.com/microsoft/confidential-sidecar-containers/releases/latest/download/skr > skr && chmod +x skr", stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, input="", shell=True)

    with tempfile.NamedTemporaryFile() as f:
        f.write(b"Oceans are full of water\nHorses have 4 legs")
        f.seek(0)

        subprocess.run(f"./skr --infile {f.name} --keypath {key} --outfile ./key_release/infile", stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, input="", shell=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    # log into Azure CLI
    subprocess.run("az login --service-principal --username $AZURE_SERVICE_PRINCIPAL_APP_ID --password $AZURE_SERVICE_PRINCIPAL_PASSWORD --tenant $AZURE_SERVICE_PRINCIPAL_TENANT", stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, input="", shell=True)

    # generate RSA key
    key_name = args.run_id + "-key"
    generate_rsa_key(key_name)

    # need generated wrapped data before creating and pushing "primary" image
    generate_wrapped_data(key_name)

    # remove key files
    os.remove(key_name + "-pub.pem")
    os.remove(key_name + "-info.json")