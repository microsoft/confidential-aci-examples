import argparse
import json
import os
from typing import Optional


def generate_arm_template(
    id: str,
    name: str,
    manifest: dict,
    location: str,
    security_policy: Optional[str] = None,
    out: Optional[str] = None,
):
    def resolve_variable(value: str):
        return os.environ[value.strip("$")] if "$" in value else value

    arm_template = {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {},
        "variables": {},
        "resources": [
            {
                "type": "Microsoft.ContainerInstance/containerGroups",
                "apiVersion": "2023-05-01",
                "name": f"group-{name}".replace("_", "-"),
                "location": location,
                "tags": {
                    "Owner": "c-aci-examples",
                    "GithubRepo": "microsoft/c-aci-examples",
                },
                "properties": {
                    "sku": "Confidential",
                    "containers": [
                        {
                            "name": f"container-{name}-{idx}".replace("_", "-"),
                            "properties": {
                                "image": container["image"].split("://")[1]
                                if container["image"].startswith("http")
                                else f'caciexamples.azurecr.io/{manifest["testName"]}/{container["image"]}:{id}',
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
                            "server": server,
                            "username": resolve_variable(credentials["username"]),
                            "password": resolve_variable(credentials["password"]),
                        }
                        for server, credentials in manifest[
                            "registryCredentials"
                        ].items()
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
        "--name",
        help="The name to use for the resources",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--manifest-path",
        help="The image to deploy the container with",
        required=True,
    )
    parser.add_argument(
        "--location",
        help="The location of the container to deploy",
        default="eastus2euap",
    )
    parser.add_argument(
        "--security-policy",
        help="The security policy to use for the container",
    )
    parser.add_argument(
        "--out",
        help="Path to save the ARM template to",
    )

    args = parser.parse_args()

    with open(args.manifest_path, "r") as manifest_file:
        generate_arm_template(
            id=args.id,
            name=args.name,
            location=args.location,
            manifest=json.load(manifest_file),
            security_policy=args.security_policy,
            out=args.out,
        )
