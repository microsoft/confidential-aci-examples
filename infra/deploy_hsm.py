# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse
import json
import os
import subprocess
import sys
from typing import Iterable
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from infra.clients import get_resource_client
from infra.deploy_arm_template import deploy_arm_template


def populate_hsm_cert_files(out_path: str) -> Iterable[str]:
    key_paths = [os.path.join(out_path, f"key-{i}.cer") for i in range(3)]
    keys = os.environ["AZURE_HSM_PUBLIC_KEYS"].split("

")
    for key_path in key_paths:
        with open(key_path, "w") as f:
            f.write(keys.pop(0))
    return key_paths


def generate_hsm_arm_template(
    name: str,
    tenant_id: str,
    admin_ids: Iterable[str],
    out: str,
):
    arm_template = {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "variables": {},
        "resources": [
            {
                "type": "Microsoft.KeyVault/managedHSMs",
                "apiVersion": "2023-02-01",
                "name": name,
                "location": "westeurope",
                "sku": {"name": "Standard_B1", "family": "B"},
                "properties": {
                    "tenantId": tenant_id,
                    "initialAdminObjectIds": admin_ids,
                    "enableSoftDelete": True,
                    "softDeleteRetentionInDays": 7,
                    "enablePurgeProtection": False,
                    "networkAcls": {
                        "bypass": "AzureServices",
                        "defaultAction": "Allow",
                        "ipRules": [],
                        "virtualNetworkRules": [],
                    },
                    "publicNetworkAccess": "Enabled",
                    "regions": [],
                },
            }
        ],
    }

    with open(out, "w") as f:
        f.write(json.dumps(arm_template, indent=2))

    return arm_template


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument(
        "--tenant-id",
        default=os.environ["MICROSOFT_TENANT_ID"],
    )
    parser.add_argument(
        "--admin-ids",
        default=[
            os.environ["AZURE_SERVICE_PRINCIPAL_OBJECT_ID"],
            os.environ["AZURE_MANAGED_IDENTITY_ID"],
        ],
        nargs="+",
    )
    parser.add_argument("--out", default=os.path.abspath("examples/key_release"))

    args = parser.parse_args()

    # Deploy the HSM resource
    deploy_arm_template(
        resource_client=get_resource_client(os.environ["AZURE_SUBSCRIPTION_ID"]),
        arm_template=generate_hsm_arm_template(
            name=args.name,
            tenant_id=args.tenant_id,
            admin_ids=args.admin_ids,
            out=os.path.join(args.out, "hsm_arm_template.json"),
        ),
        resource_group=os.environ["AZURE_RESOURCE_GROUP"],
        deployment_name=f"{uuid.uuid4()}-hsm-deployment",
    )

    # Activate the HSM
    subprocess.check_call(
        " ".join(
            [
                "az keyvault security-domain download",
                f"--hsm-name {args.name}",
                "--sd-quorum 3",
                f"--sd-wrapping-keys {' '.join(populate_hsm_cert_files(args.out))}",
                f"--security-domain-file {os.path.join(args.out, 'security_domain.json')}",
            ]
        ),
        shell=True,
    )

    # Add the roles to the HSM
    for user in args.admin_ids:
        for role in ["Managed HSM Crypto User", "Managed HSM Crypto Officer"]:
            subprocess.run(
                " ".join(
                    [
                        "az keyvault role assignment create",
                        f"--hsm-name {args.name}",
                        f'--role "{role}"',
                        f"--assignee-object-id {user}",
                        "--scope /keys",
                    ]
                ),
                shell=True,
            )
