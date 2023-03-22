"""Deploy a Confidential Azure Container Instance for use in the examples."""

from argparse import ArgumentParser
from typing import Optional
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from functools import lru_cache


@lru_cache
def get_resource_client(subscription_id: str) -> ResourceManagementClient:
    return ResourceManagementClient(DefaultAzureCredential(), subscription_id)


@lru_cache
def get_container_client(subscription_id: str) -> ContainerInstanceManagementClient:
    return ContainerInstanceManagementClient(DefaultAzureCredential(), subscription_id)


def deploy_aci(
    resource_client: ResourceManagementClient,
    resource_group: str,
    name: str,
    image: str,
    registry_password: str,
):
    """Deploy a Confidential Azure Container Instance for use in the examples."""

    resource_client.deployments.begin_create_or_update(
        resource_group,
        name,
        {
            "properties": {
                "template": {
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
                                            "resources": {
                                                "requests": {"memoryInGB": 16, "cpu": 4}
                                            },
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
                                    "ccePolicy": "cGFja2FnZSBwb2xpY3kKCmFwaV9zdm4gOj0gIjAuMTAuMCIKZnJhbWV3b3JrX3N2biA6PSAiMC4xLjAiCgptb3VudF9kZXZpY2UgOj0geyJhbGxvd2VkIjogdHJ1ZX0KbW91bnRfb3ZlcmxheSA6PSB7ImFsbG93ZWQiOiB0cnVlfQpjcmVhdGVfY29udGFpbmVyIDo9IHsiYWxsb3dlZCI6IHRydWUsICJhbGxvd19zdGRpb19hY2Nlc3MiOiB0cnVlfQp1bm1vdW50X2RldmljZSA6PSB7ImFsbG93ZWQiOiB0cnVlfQp1bm1vdW50X292ZXJsYXkgOj0geyJhbGxvd2VkIjogdHJ1ZX0KZXhlY19pbl9jb250YWluZXIgOj0geyJhbGxvd2VkIjogdHJ1ZX0KZXhlY19leHRlcm5hbCA6PSB7ImFsbG93ZWQiOiB0cnVlLCAiYWxsb3dfc3RkaW9fYWNjZXNzIjogdHJ1ZX0Kc2h1dGRvd25fY29udGFpbmVyIDo9IHsiYWxsb3dlZCI6IHRydWV9CnNpZ25hbF9jb250YWluZXJfcHJvY2VzcyA6PSB7ImFsbG93ZWQiOiB0cnVlfQpwbGFuOV9tb3VudCA6PSB7ImFsbG93ZWQiOiB0cnVlfQpwbGFuOV91bm1vdW50IDo9IHsiYWxsb3dlZCI6IHRydWV9CmdldF9wcm9wZXJ0aWVzIDo9IHsiYWxsb3dlZCI6IHRydWV9CmR1bXBfc3RhY2tzIDo9IHsiYWxsb3dlZCI6IHRydWV9CnJ1bnRpbWVfbG9nZ2luZyA6PSB7ImFsbG93ZWQiOiB0cnVlfQpsb2FkX2ZyYWdtZW50IDo9IHsiYWxsb3dlZCI6IHRydWV9CnNjcmF0Y2hfbW91bnQgOj0geyJhbGxvd2VkIjogdHJ1ZX0Kc2NyYXRjaF91bm1vdW50IDo9IHsiYWxsb3dlZCI6IHRydWV9Cg=="
                                },
                                "imageRegistryCredentials": [
                                    {
                                        "server": "caciexamples.azurecr.io",
                                        "username": "caciexamples",
                                        "password": {registry_password},
                                    }
                                ],
                            },
                        }
                    ],
                },
                "parameters": {},
                "mode": "Incremental",
            }
        },
    ).wait()


def get_aci_ip(
    resource_client: ResourceManagementClient,
    container_client: ContainerInstanceManagementClient,
    resource_group: str,
    name: str,
) -> Optional[str]:
    try:
        deployment = resource_client.deployments.get(
            resource_group,
            name,
        )
    except Exception as e:
        return None

    for resource in deployment.properties.output_resources:
        container_group_name = resource.id.split("/")[-1]
        container_group = container_client.container_groups.get(
            resource_group, container_group_name
        )

    return container_group.ip_address.ip


def remove_aci(
    resource_client: ResourceManagementClient,
    container_client: ContainerInstanceManagementClient,
    resource_group: str,
    name: str,
    asynchronous: bool = False,
):
    """Remove the Confidential Azure Container Instance."""
    deployment = resource_client.deployments.get(
        resource_group,
        name,
    )

    for resource in deployment.properties.output_resources:
        container_name = resource.id.split("/")[-1]
        delete_op = container_client.container_groups.begin_delete(
            resource_group,
            container_name,
        )
        if not asynchronous:
            delete_op.wait()

    delete_op = resource_client.deployments.begin_delete(resource_group, name)
    if not asynchronous:
        delete_op.wait()


def _parse_args():
    parser = ArgumentParser()

    parser.add_argument(
        "operation",
        help="Whether to deploy or remove the ACI.",
        type=str,
        choices=[
            "deploy",
            "get_ip",
            "remove",
        ],
    )
    parser.add_argument(
        "--subscription-id",
        help="The subscription to deploy the ACI with.",
        required=True,
        type=str,
    )
    parser.add_argument(
        "--resource-group",
        help="The resource group to deploy the ACI with.",
        required=True,
        type=str,
    )
    parser.add_argument(
        "--name",
        help="The name of the ACI to deploy.",
        required=True,
        type=str,
    )
    parser.add_argument(
        "--image",
        help="The URL for the container image to deploy.",
        type=str,
    )
    parser.add_argument(
        "--registry-password",
        help="The password to the registry to push images to.",
        type=str,
    )

    return parser.parse_args()


if __name__ == "__main__":
    _args = _parse_args()

    if _args.operation == "deploy":
        deploy_aci(
            resource_client=get_resource_client(_args.subscription_id),
            resource_group=_args.resource_group,
            name=_args.name,
            image=_args.image,
            registry_password=_args.registry_password,
        )
    elif _args.operation == "get_ip":
        print(
            get_aci_ip(
                resource_client=get_resource_client(_args.subscription_id),
                container_client=get_container_client(_args.subscription_id),
                resource_group=_args.resource_group,
                name=_args.name,
            )
        )
    elif _args.operation == "remove":
        remove_aci(
            resource_client=get_resource_client(_args.subscription_id),
            container_client=get_container_client(_args.subscription_id),
            resource_group=_args.resource_group,
            name=_args.name,
        )
