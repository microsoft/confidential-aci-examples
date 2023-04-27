import argparse
import json
import os
from typing import Optional


def generate_arm_template(
    id: str,
    container_group_name: str,
    location: str,
    manifest: dict,
    registry_password: Optional[str] = None,
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
                "name": container_group_name,
                "location": location,
                "tags": {
                    "Owner": "c-aci-examples",
                    "GithubRepo": "microsoft/c-aci-examples",
                },
                "properties": {
                    "sku": "Confidential",
                    "containers": [
                        {
                            "name": f"{container_group_name}-{idx}",
                            "properties": {
                                "image": f'caciexamples.azurecr.io/{manifest["testName"]}/{container["repository"]}:{id}',
                                "ports": [
                                    {"protocol": "TCP", "port": port}
                                    for port in container["ports"]
                                ],
                                "environmentVariables": [],
                                "resources": {
                                    "requests": {
                                        "memoryInGB": container["ram"],
                                        "cpu": container["cores"],
                                    }
                                },
                            },
                        }
                        for idx, container in enumerate(container_group["containers"])
                    ],
                    "initContainers": [],
                    "restartPolicy": "Never",
                    "osType": "Linux",
                    "ipAddress": {
                        "ports": [
                            {"protocol": "TCP", "port": port}
                            for port in container_group["ports"]
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
                            "password": registry_password
                            or os.getenv("AZ_REGISTRY_PASSWORD", ""),
                        }
                    ],
                },
            }
            for container_group in manifest["containerGroups"]
        ],
    }

    if out:
        with open(out, "w") as f:
            f.write(json.dumps(arm_template, indent=2))

    return arm_template


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate ARM template")
    parser.add_argument(
        "--id",
        help="The ID to use for the image tag",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--container-group-name",
        help="The name of the container group to deploy",
        required=True,
    )
    parser.add_argument(
        "--location",
        help="The location of the container to deploy",
        default="eastus2euap",
    )
    parser.add_argument(
        "--manifest-path",
        help="The image to deploy the container with",
        required=True,
    )
    parser.add_argument(
        "--security-policy",
        help="The security policy to use for the container",
    )
    parser.add_argument(
        "--registry-password",
        help="The password to the container registry containing the image",
    )
    parser.add_argument(
        "--out",
        help="Path to save the ARM template to",
    )

    args = parser.parse_args()

    with open(args.manifest_path, "r") as manifest_file:
        manifest = json.load(manifest_file)
        generate_arm_template(
            id=args.id,
            container_group_name=args.container_group_name,
            location=args.location,
            manifest=manifest,
            registry_password=args.registry_password,
            out=args.out,
            security_policy=args.security_policy,
        )
