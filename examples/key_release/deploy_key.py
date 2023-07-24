import argparse
from base64 import b64encode, b64decode
import binascii
import hashlib
import json
import os
import secrets
import subprocess
import requests


def deploy_key(arm_template: dict):
    name = None
    for resource in arm_template["resources"]:
        for container in resource["properties"]["containers"]:
            for env_var in container["properties"]["environmentVariables"]:
                if env_var["name"] == "SkrClientKID":
                    name = env_var["value"]
                    break
    assert name is not None

    resources = arm_template["resources"]
    assert len(resources) == 1

    security_policy_digest = hashlib.sha256(
        b64decode(
            resources[0]["properties"]["confidentialComputeProperties"]["ccePolicy"]
        )
    ).hexdigest()

    response = requests.put(
        url=f"https://{os.environ['AZURE_HSM_ENDPOINT']}/keys/{name}?api-version=7.3-preview",
        data=json.dumps(
            {
                "key": {
                    "kty": "oct-HSM",
                    "k": binascii.hexlify(secrets.token_bytes(32)).decode(),
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
                                "version": "0.2",
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
    print(f"Deployed key {name}-key into the HSM")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm-template-path", required=True)
    args = parser.parse_args()

    with open(args.arm_template_path, "r") as f:
        deploy_key(json.load(f))
