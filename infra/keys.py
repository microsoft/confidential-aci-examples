# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from base64 import urlsafe_b64encode, b64encode, b64decode
import binascii
import hashlib
import json
import os
import sys
from io import BufferedWriter
import subprocess
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def deploy_key(name: str, arm_template: dict, key: bytes):
    resources = arm_template["resources"]
    assert len(resources) == 1

    security_policy_digest = hashlib.sha256(
        b64decode(
            resources[0]["properties"]["confidentialComputeProperties"]["ccePolicy"]
        )
    ).hexdigest()

    response = requests.put(
        url=f"https://{os.environ['AZURE_HSM_ENDPOINT']}/keys/{name}?api-version=7.4",
        data=json.dumps(
            {
                "key": {
                    "kty": "oct-HSM",
                    "k": urlsafe_b64encode(binascii.unhexlify(key)).decode(),
                    "key_size": 256,
                },
                "hsm": True,
                "attributes": {
                    "exportable": True,
                },
                "release_policy": {
                    "contentType": "application/json; charset=utf-8",
                    "data": b64encode(
                        json.dumps(
                            {
                                "version": "1.0.0",
                                "anyOf": [
                                    {
                                        "authority": f"https://{os.environ['AZURE_ATTESTATION_ENDPOINT']}",
                                        "allOf": [
                                            {
                                                "claim": "x-ms-sevsnpvm-hostdata",
                                                "equals": security_policy_digest,
                                            },
                                            {
                                                "claim": "x-ms-compliance-status",
                                                "equals": "azure-compliant-uvm",
                                            },
                                            {
                                                "claim": "x-ms-sevsnpvm-is-debuggable",
                                                "equals": "false",
                                            },
                                        ],
                                    }
                                ],
                            }
                        ).encode()
                    ).decode(),
                    "immutable": False,
                },
            }
        ),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer "
            + json.loads(
                subprocess.check_output(
                    "az account get-access-token --resource https://managedhsm.azure.net",
                    shell=True,
                )
            )["accessToken"],
        },
    )

    assert response.status_code == 200, response.content
    print(f"Deployed key {name} into the HSM")


def generate_key_file(tmp_key_file: BufferedWriter):
    print("Generating key file")
    subprocess.check_call(
        f"dd if=/dev/random of={tmp_key_file.name} count=1 bs=32", shell=True
    )

    print("Getting key in hex string format")
    bData = tmp_key_file.read(32)

    subprocess.check_call(f"truncate -s 32 {tmp_key_file.name}", shell=True)
    return binascii.hexlify(bData)
