import argparse
import json
import os
from typing import Optional


def generate_arm_template(
    name: str,
    image: str,
    out: Optional[str] = None,
    security_policy: Optional[str] = None,
):
    arm_template = {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {},
        "variables": {},
        "resources": [
            {
                "type": "Microsoft.ContainerInstance/containerGroups",
                "apiVersion": "2022-10-01-preview",
                "name": f"{name}",
                "location": "eastus2euap",
                "tags": {
                    "Owner": "c-aci-examples",
                    "GithubRepo": "microsoft/c-aci-examples",
                },
                "properties": {
                    "sku": "Confidential",
                    "containers": [
                        {
                            "name": f"{name}-0",
                            "properties": {
                                "image": image,
                                "ports": [
                                    {"protocol": "TCP", "port": "22"},
                                    {"protocol": "TCP", "port": "8000"},
                                ],
                                "environmentVariables": [],
                                "resources": {"requests": {"memoryInGB": 16, "cpu": 4}},
                            },
                        }
                    ],
                    "initContainers": [],
                    "restartPolicy": "Never",
                    "osType": "Linux",
                    "ipAddress": {
                        "ports": [
                            {"protocol": "TCP", "port": "22"},
                            {"protocol": "TCP", "port": "8000"},
                        ],
                        "type": "Public",
                    },
                    "confidentialComputeProperties": {
                        "ccePolicy": security_policy,
                    },
                    "imageRegistryCredentials": [
                        {
                            "server": "caciexamples.azurecr.io",
                            "username": "caciexamples",
                            "password": os.getenv("AZ_REGISTRY_PASSWORD"),
                        }
                    ],
                },
            }
        ],
    }

    template_str = json.dumps(arm_template, indent=2)
    print(template_str)

    if out:
        with open(out, "w") as f:
            f.write(template_str)

    return arm_template


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate ARM template")
    parser.add_argument(
        "--name",
        help="The name of the container to deploy",
        required=True,
    )
    parser.add_argument(
        "--image",
        help="The image to deploy the container with",
        required=True,
    )
    parser.add_argument(
        "--security-policy",
        help="The security policy to use for the container",
    )
    parser.add_argument(
        "--out",
        help="Path to save the ARM template to",
    )

    generate_arm_template(**vars(parser.parse_args()))