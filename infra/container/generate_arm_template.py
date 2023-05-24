import argparse
import json
import os
from typing import Optional
import uuid


def generate_arm_template(
    name: str,
    image_tag: str,
    manifest: dict,
    location: str,
    security_policy: Optional[str] = None,
    out: Optional[str] = None,
):
    def resolve_variable(value: str):
        return os.environ[value.strip("$")] if "$" in value else value

    print(f"Generating ARM template for {name}")
    arm_template = {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {},
        "variables": {},
        "resources": [
            {
                "type": "Microsoft.ContainerInstance/containerGroups",
                "apiVersion": "2023-05-01",
                "name": name.replace("_", "-"),
                "location": location,
                "tags": {
                    "Owner": "c-aci-examples",
                    "GithubRepo": "microsoft/c-aci-examples",
                },
                "properties": {
                    "sku": "Confidential",
                    "containers": [
                        {
                            "name": f"{name}-{idx}".replace("_", "-"),
                            "properties": {
                                "image": container["image"].split("://")[1]
                                if container["image"].startswith("http")
                                else f'{os.environ["AZURE_REGISTRY_URL"]}/{manifest["testName"]}/{container["image"]}:{image_tag}',
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
                            "server": resolve_variable(server),
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
    print("Done")

    if out:
        print(f"Saving ARM template to {out}")
        with open(out, "w") as f:
            f.write(json.dumps(arm_template, indent=2))

    return arm_template


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate ARM template")
    parser.add_argument(
        "--name",
        help="The name to use for the resources",
        type=str,
    )
    parser.add_argument(
        "--image-tag",
        help="The image tags to use",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--manifest-path",
        help="The manifest to generate an ARM template for",
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
        manifest = json.load(manifest_file)
        generate_arm_template(
            name=args.name or f"group-{uuid.uuid4()}",
            image_tag=args.image_tag,
            location=args.location,
            manifest=manifest,
            security_policy=args.security_policy,
            out=args.out,
        )