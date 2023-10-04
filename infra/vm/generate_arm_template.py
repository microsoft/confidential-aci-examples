# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse
import json
import os
from typing import Optional
import uuid
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.read_manifest_ports import read_manifest_ports


def generate_arm_template(
    name: str,
    password: str,
    manifest: dict,
    location: str,
    out: Optional[str] = None,
):
    with open(os.path.expanduser("~/.ssh/id_rsa.pub")) as ssh_key_file:
        ssh_key = ssh_key_file.read().rstrip("\n")

    ports = read_manifest_ports(manifest)
    arm_template = {
        "$schema": "http://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "variables": {
            "uniqueId": name,
            "vmPassword": password,
            "nsgId": f"[resourceId(resourceGroup().name, 'Microsoft.Network/networkSecurityGroups', '{name}-nsg')]",
            "vnetId": f"[resourceId(resourceGroup().name, 'Microsoft.Network/virtualNetworks', '{name}-vnet')]",
            "ipId": f"[resourceId(resourceGroup().name, 'Microsoft.Network/publicIpAddresses', '{name}-ip')]",
            "subnetRef": f"[concat(variables('vnetId'), '/subnets/', '{name}-subnet')]",
            "containerPorts": list(ports),
        },
        "resources": [
            {
                "type": "Microsoft.Network/networkInterfaces",
                "apiVersion": "2021-08-01",
                "name": f"{name}-ni",
                "location": location,
                "dependsOn": [
                    f"[concat('Microsoft.Network/networkSecurityGroups/', '{name}-nsg')]",
                    f"[concat('Microsoft.Network/virtualNetworks/', '{name}-vnet')]",
                    f"[concat('Microsoft.Network/publicIpAddresses/', '{name}-ip')]",
                ],
                "properties": {
                    "ipConfigurations": [
                        {
                            "name": "ipconfig1",
                            "properties": {
                                "subnet": {"id": "[variables('subnetRef')]"},
                                "privateIPAllocationMethod": "Dynamic",
                                "publicIpAddress": {
                                    "id": "[variables('ipId')]",
                                    "properties": {"deleteOption": "Delete"},
                                },
                            },
                        }
                    ],
                    "networkSecurityGroup": {"id": "[variables('nsgId')]"},
                },
            },
            {
                "name": f"{name}-nsg",
                "type": "Microsoft.Network/networkSecurityGroups",
                "apiVersion": "2019-02-01",
                "location": location,
                "properties": {
                    "securityRules": [
                        {
                            "name": "RDP",
                            "properties": {
                                "priority": 300,
                                "protocol": "TCP",
                                "access": "Allow",
                                "direction": "Inbound",
                                "sourceAddressPrefix": "*",
                                "sourcePortRange": "*",
                                "destinationAddressPrefix": "*",
                                "destinationPortRange": "3389",
                            },
                        },
                        {
                            "name": "SSH",
                            "properties": {
                                "priority": 320,
                                "protocol": "TCP",
                                "access": "Allow",
                                "direction": "Inbound",
                                "sourceAddressPrefix": "*",
                                "sourcePortRange": "*",
                                "destinationAddressPrefix": "*",
                                "destinationPortRange": "22",
                            },
                        },
                        {
                            "name": "HTTPS",
                            "properties": {
                                "priority": 340,
                                "protocol": "TCP",
                                "access": "Allow",
                                "direction": "Inbound",
                                "sourceAddressPrefix": "*",
                                "sourcePortRange": "*",
                                "destinationAddressPrefix": "*",
                                "destinationPortRange": "443",
                            },
                        },
                        {
                            "name": "HTTP",
                            "properties": {
                                "priority": 360,
                                "protocol": "TCP",
                                "access": "Allow",
                                "direction": "Inbound",
                                "sourceAddressPrefix": "*",
                                "sourcePortRange": "*",
                                "destinationAddressPrefix": "*",
                                "destinationPortRange": "80",
                            },
                        },
                        {
                            "name": "Payload-HTTP",
                            "properties": {
                                "priority": 370,
                                "protocol": "TCP",
                                "access": "Allow",
                                "direction": "Inbound",
                                "sourceAddressPrefix": "*",
                                "sourcePortRange": "*",
                                "destinationAddressPrefix": "*",
                                "destinationPortRanges": "[variables('containerPorts')]",
                            },
                        },
                    ]
                },
            },
            {
                "name": f"{name}-vnet",
                "type": "Microsoft.Network/virtualNetworks",
                "apiVersion": "2021-01-01",
                "location": location,
                "properties": {
                    "addressSpace": {"addressPrefixes": ["10.0.0.0/16"]},
                    "subnets": [
                        {
                            "name": f"{name}-subnet",
                            "properties": {"addressPrefix": "10.0.0.0/24"},
                        }
                    ],
                },
            },
            {
                "name": f"{name}-ip",
                "type": "Microsoft.Network/publicIpAddresses",
                "apiVersion": "2020-08-01",
                "location": location,
                "properties": {"publicIpAllocationMethod": "Static"},
                "sku": {"name": "Standard"},
                "zones": ["2"],
            },
            {
                "name": f"{name}-vm",
                "type": "Microsoft.Compute/virtualMachines",
                "apiVersion": "2022-03-01",
                "location": location,
                "dependsOn": [
                    f"[concat('Microsoft.Network/networkInterfaces/', '{name}-ni')]"
                ],
                "properties": {
                    "hardwareProfile": {"vmSize": "Standard_DC4ads_cc_v5"},
                    "storageProfile": {
                        "osDisk": {
                            "createOption": "fromImage",
                            "managedDisk": {"storageAccountType": "Premium_LRS"},
                            "deleteOption": "Delete",
                        },
                        "imageReference": {
                            "id": "/subscriptions/268b7184-1452-4a31-ac9f-6a408da360b5/resourceGroups/AtlasImageGallery/providers/Microsoft.Compute/galleries/AtlasImageGallery/images/AtlasSNPimage/versions/2023.0921.1"
                        },
                    },
                    "networkProfile": {
                        "networkInterfaces": [
                            {
                                "id": f"[resourceId('Microsoft.Network/networkInterfaces', '{name}-ni')]",
                                "properties": {"deleteOption": "Delete"},
                            }
                        ]
                    },
                    "osProfile": {
                        "computerName": "test-machine",
                        "adminUsername": "test-user",
                        "adminPassword": password,
                        "windowsConfiguration": {
                            "enableAutomaticUpdates": True,
                            "provisionVmAgent": True,
                            "patchSettings": {
                                "enableHotpatching": "False",
                                "patchMode": "AutomaticByOS",
                            },
                        },
                    },
                    "diagnosticsProfile": {"bootDiagnostics": {"enabled": True}},
                },
                "zones": ["2"],
            },
            {
                "name": f"shutdown-computevm-{name}-vm",
                "type": "Microsoft.DevTestLab/schedules",
                "apiVersion": "2018-09-15",
                "location": location,
                "dependsOn": [
                    f"[concat('Microsoft.Compute/virtualMachines/', '{name}-vm')]"
                ],
                "properties": {
                    "status": "Enabled",
                    "taskType": "ComputeVmShutdownTask",
                    "dailyRecurrence": {"time": "19:00"},
                    "timeZoneId": "UTC",
                    "targetResourceId": f"[resourceId('Microsoft.Compute/virtualMachines', '{name}-vm')]",
                },
            },
            {
                "name": f"{name}-vm/RunPowerShellScript",
                "type": "Microsoft.Compute/virtualMachines/runCommands",
                "apiVersion": "2022-03-01",
                "location": location,
                "dependsOn": [
                    f"[concat('Microsoft.Compute/virtualMachines/', '{name}-vm')]"
                ],
                "properties": {
                    "source": {
                        "script": "; ".join(
                            [
                                "Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0",
                                "Start-Service sshd",
                                f'{ssh_key} | Add-Content "C:\ProgramData\ssh\administrators_authorized_keys" /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F"',
                                "Enable-WindowsOptionalFeature -Online -All -FeatureName Microsoft-Hyper-V, Containers",
                                f'New-NetFirewallRule -DisplayName "Allow Payload Ports" -Direction Inbound -LocalPort {",".join([str(p) for p in ports])} -Protocol TCP -Action Allow',
                            ]
                        )
                    },
                },
            },
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
        "--location",
        help="The location of the container to deploy",
        default="westeurope",
    )
    parser.add_argument(
        "--manifest-path",
        help="The manifest to generate an ARM template for",
        required=True,
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
        password=str(uuid.uuid4()),
        manifest=manifest,
        location=args.location,
        out=args.out,
    )
