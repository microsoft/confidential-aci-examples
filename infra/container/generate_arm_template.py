# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse
from base64 import b64encode, b64decode
import json
import os
import sys
from typing import Optional
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.resolve_manifest_variables import resolve_manifest_variables


def generate_arm_template(
    name: str,
    image_tag: str,
    manifest: dict,
    location: str,
    security_policy: Optional[str] = None,
    out: Optional[str] = None,
):
    if "UNIQUE_ID" not in os.environ:
        os.environ["UNIQUE_ID"] = name
    manifest = resolve_manifest_variables(manifest)

    if security_policy:
        raw_policy = b64decode(security_policy)
        security_policy = [
            b64encode(f"package{policy}".encode()).decode()
            for policy in raw_policy.decode().split("package")[1:]
        ]
        assert len(manifest["containerGroups"]) == len(
            security_policy
        ), f"{security_policy=} doesn't match {manifest['containerGroups']=}"
    else:
        security_policy = [None for _ in range(len(manifest["containerGroups"]))]

    print(f"Generating ARM template for {name}")
    arm_template = {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {},
        "variables": {
            "uniqueId": name,
        },
        "resources": [
            {
                "type": "Microsoft.ContainerInstance/containerGroups",
                "apiVersion": "2023-05-01",
                "name": f"{name}-group-{group_idx}".replace("_", "-"),
                "location": location,
                "tags": {
                    "Owner": "c-aci-examples",
                    "GithubRepo": "microsoft/c-aci-examples",
                },
                "identity": {
                    "type": "UserAssigned",
                    "userAssignedIdentities": {
                        "[resourceId('Microsoft.ManagedIdentity/userAssignedIdentities', 'caciexamples')]": {},
                    },
                },
                "properties": {
                    "sku": "Confidential",
                    "containers": [
                        {
                            "name": f"{name}-container-{idx}".replace("_", "-"),
                            "properties": {
                                "image": container["image"].split("://")[1]
                                if container["image"].startswith("http")
                                else f'{os.environ["AZURE_REGISTRY_URL"]}/{manifest["testName"]}/{container["image"]}:{image_tag}',
                                "ports": [
                                    {"protocol": "TCP", "port": port}
                                    for port in container["ports"]
                                ]
                                if "ports" in container
                                else [],
                                "securityContext": {
                                    "privileged": container.get("privileged", False)
                                },
                                "volumeMounts": [
                                    {
                                        "name": volumeName,
                                        "mountPath": volumePath,
                                    }
                                    for volumeName, volumePath in container.get(
                                        "mounts", {}
                                    ).items()
                                ],
                                "environmentVariables": [
                                    {"name": k, "value": v}
                                    for k, v in (container.get("env") or {}).items()
                                ],
                                "resources": {
                                    "requests": {
                                        "memoryInGB": container["ram"],
                                        "cpu": container["cores"],
                                    }
                                },
                                **(
                                    {"command": container.get("command")}
                                    if "command" in container
                                    else {}
                                ),
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
                    "volumes": [
                        {
                            "name": volume,
                            "emptyDir": {},
                        }
                        for volume in container_group.get("volumes", [])
                    ],
                    "confidentialComputeProperties": {
                        "ccePolicy": security_policy[group_idx],
                    },
                    "imageRegistryCredentials": [
                        {
                            "server": server,
                            "username": credentials["username"],
                            "password": credentials["password"],
                        }
                        for server, credentials in manifest[
                            "registryCredentials"
                        ].items()
                    ],
                },
            }
            for group_idx, container_group in enumerate(manifest["containerGroups"])
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
        default="westeurope",
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
            name=args.name or str(uuid.uuid4()),
            image_tag=args.image_tag,
            location=args.location,
            manifest=manifest,
            security_policy=args.security_policy,
            out=args.out,
        )
