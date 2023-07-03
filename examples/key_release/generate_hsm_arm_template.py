import argparse
import json
import os
from typing import Iterable


def generate_hsm_arm_template(
    name: str,
    tenant_id: str,
    admin_ids: Iterable[str],
    out: str,
):
    arm_template = {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {
            "managedHSMs_caciexamples_name": {
                "defaultValue": "caciexamples",
                "type": "String",
            }
        },
        "variables": {},
        "resources": [
            {
                "type": "Microsoft.KeyVault/managedHSMs",
                "apiVersion": "2023-02-01",
                "name": name,
                "location": "eastus",
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
    parser.add_argument("--tenant-id", required=True)
    parser.add_argument("--admin-ids", nargs="+", required=True)
    parser.add_argument("--out", required=True)

    args = parser.parse_args()

    generate_hsm_arm_template(
        name=args.name,
        tenant_id=args.tenant_id,
        admin_ids=args.admin_ids,
        out=args.out,
    )
