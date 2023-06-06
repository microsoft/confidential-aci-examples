import argparse
import json
import os
from typing import Optional
import uuid


def generate_arm_template(
    name: str,
    location: str,
    out: Optional[str] = None,
):
    password = str(uuid.uuid4())
    with open(os.path.expanduser("~/.ssh/id_rsa.pub")) as ssh_key_file:
        ssh_key = ssh_key_file.read().rstrip("\n")

    print(f"Generating ARM template for {name} and password '{password}'")
    arm_template = {
        "$schema": "http://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "variables": {
            "uniqueId": name,
            "vmPassword": password,
            "nsgId": f"[resourceId(resourceGroup().name, 'Microsoft.Network/networkSecurityGroups', '{name}-nsg')]",
            "vnetId": f"[resourceId(resourceGroup().name, 'Microsoft.Network/virtualNetworks', '{name}-vnet')]",
            "ipId": f"[resourceId(resourceGroup().name, 'Microsoft.Network/publicIpAddresses', '{name}-ip')]",
            "subnetRef": "[concat(variables('vnetId'), '/subnets/', 'default')]",
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
                            "name": "default",
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
                            "id": "/subscriptions/268b7184-1452-4a31-ac9f-6a408da360b5/resourceGroups/AtlasImageGallery/providers/Microsoft.Compute/galleries/AtlasImageGallery/images/AtlasSNPimage/versions/2023.03.20348"
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
                        "script": f'Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0; Start-Service sshd; {ssh_key} | Add-Content "C:\\ProgramData\\ssh\\administrators_authorized_keys";icacls.exe "C:\\ProgramData\\ssh\\administrators_authorized_keys" /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F"; Enable-WindowsOptionalFeature -Online -All -FeatureName Microsoft-Hyper-V, Containers',
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
        default="eastus2euap",
    )
    parser.add_argument(
        "--out",
        help="Path to save the ARM template to",
    )

    args = parser.parse_args()

    generate_arm_template(
        name=args.name or f"{uuid.uuid4()}",
        location=args.location,
        out=args.out,
    )
