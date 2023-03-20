"""Deploy a Confidential Azure Container Instance for use in the examples."""

from argparse import ArgumentParser
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.containerinstance import ContainerInstanceManagementClient


def deploy_aci(
    resource_client: ResourceManagementClient,
    resource_group: str,
    name: str,
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
                                            "image": "mcr.microsoft.com/mirror/docker/library/ubuntu:22.04",
                                            "command": [
                                                "/bin/sh",
                                                "-c",
                                                "tail -f /dev/null",
                                            ],
                                            "ports": [
                                                {"protocol": "TCP", "port": "22"}
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
                                "confidentialComputeProperties": {
                                    "ccePolicy": "cGFja2FnZSBwb2xpY3kKCmFwaV9zdm4gOj0gIjAuMTAuMCIKZnJhbWV3b3JrX3N2biA6PSAiMC4xLjAiCgptb3VudF9kZXZpY2UgOj0geyJhbGxvd2VkIjogdHJ1ZX0KbW91bnRfb3ZlcmxheSA6PSB7ImFsbG93ZWQiOiB0cnVlfQpjcmVhdGVfY29udGFpbmVyIDo9IHsiYWxsb3dlZCI6IHRydWUsICJhbGxvd19zdGRpb19hY2Nlc3MiOiB0cnVlfQp1bm1vdW50X2RldmljZSA6PSB7ImFsbG93ZWQiOiB0cnVlfQp1bm1vdW50X292ZXJsYXkgOj0geyJhbGxvd2VkIjogdHJ1ZX0KZXhlY19pbl9jb250YWluZXIgOj0geyJhbGxvd2VkIjogdHJ1ZX0KZXhlY19leHRlcm5hbCA6PSB7ImFsbG93ZWQiOiB0cnVlLCAiYWxsb3dfc3RkaW9fYWNjZXNzIjogdHJ1ZX0Kc2h1dGRvd25fY29udGFpbmVyIDo9IHsiYWxsb3dlZCI6IHRydWV9CnNpZ25hbF9jb250YWluZXJfcHJvY2VzcyA6PSB7ImFsbG93ZWQiOiB0cnVlfQpwbGFuOV9tb3VudCA6PSB7ImFsbG93ZWQiOiB0cnVlfQpwbGFuOV91bm1vdW50IDo9IHsiYWxsb3dlZCI6IHRydWV9CmdldF9wcm9wZXJ0aWVzIDo9IHsiYWxsb3dlZCI6IHRydWV9CmR1bXBfc3RhY2tzIDo9IHsiYWxsb3dlZCI6IHRydWV9CnJ1bnRpbWVfbG9nZ2luZyA6PSB7ImFsbG93ZWQiOiB0cnVlfQpsb2FkX2ZyYWdtZW50IDo9IHsiYWxsb3dlZCI6IHRydWV9CnNjcmF0Y2hfbW91bnQgOj0geyJhbGxvd2VkIjogdHJ1ZX0Kc2NyYXRjaF91bm1vdW50IDo9IHsiYWxsb3dlZCI6IHRydWV9Cg=="
                                },
                            },
                        }
                    ],
                },
                "parameters": {},
                "mode": "Incremental",
            }
        },
    ).wait()


def remove_aci(
    resource_client: ResourceManagementClient,
    container_client: ContainerInstanceManagementClient,
    resource_group: str,
    name: str,
):
    """Remove the Confidential Azure Container Instance."""
    deployment = resource_client.deployments.get(
        resource_group,
        name,
    )

    for resource in deployment.properties.output_resources:
        container_name = resource.id.split("/")[-1]
        container_client.container_groups.begin_delete(
            resource_group,
            container_name,
        ).wait()

    resource_client.deployments.begin_delete(resource_group, name).wait()


def _parse_args():
    arg_parser = ArgumentParser()

    arg_parser.add_argument(
        "operation",
        help="Whether to deploy or remove the ACI.",
        type=str,
        choices=[
            "deploy",
            "remove",
        ],
    )

    arg_parser.add_argument(
        "--subscription-id",
        help="The subscription to deploy the ACI with.",
        required=True,
        type=str,
    )

    arg_parser.add_argument(
        "--resource-group",
        help="The resource group to deploy the ACI with.",
        required=True,
        type=str,
    )

    arg_parser.add_argument(
        "--name",
        help="The name of the ACI to deploy.",
        required=True,
        type=str,
    )

    return arg_parser.parse_args()


if __name__ == "__main__":
    _args = _parse_args()

    _resource_client = ResourceManagementClient(
        DefaultAzureCredential(), _args.subscription_id
    )
    _container_client = ContainerInstanceManagementClient(
        DefaultAzureCredential(), _args.subscription_id
    )

    if _args.operation == "deploy":
        deploy_aci(
            resource_client=_resource_client,
            resource_group=_args.resource_group,
            name=_args.name,
        )
    elif _args.operation == "remove":
        remove_aci(
            resource_client=_resource_client,
            container_client=_container_client,
            resource_group=_args.resource_group,
            name=_args.name,
        )
