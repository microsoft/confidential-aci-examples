from base64 import b64encode, b64decode
import binascii
import hashlib
import json
import os
import secrets
import subprocess
import requests


def deploy_key():
    with open(f"examples/key_release/arm_template.json", "r") as f:
        arm_template = json.load(f)
    name = arm_template["variables"]["uniqueId"]

    resources = arm_template["resources"]
    assert len(resources) == 1

    security_policy_digest = hashlib.sha256(
        b64decode(
            resources[0]["properties"]["confidentialComputeProperties"]["ccePolicy"]
        )
    ).hexdigest()

    response = requests.put(
        url=f"https://{os.environ['AZURE_HSM_ENDPOINT']}/keys/{name}-key?api-version=7.3-preview",
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
    deploy_key()
