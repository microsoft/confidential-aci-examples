# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import Optional
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.containerinstance import ContainerInstanceManagementClient


def get_container_ip(
    resource_client: ResourceManagementClient,
    container_client: ContainerInstanceManagementClient,
    resource_group: str,
    deployment_name: str,
) -> Optional[str]:
    try:
        resources = resource_client.resources.list_by_resource_group(resource_group)
        print(f"Resources in {resource_group}: {resources}")
        deployment = resource_client.deployments.get(
            resource_group,
            deployment_name,
        )
        print(f"Deployment: {deployment}")
        assert deployment.properties.output_resources
    except Exception as e:
        print(e)
        return

    for resource in deployment.properties.output_resources:
        return container_client.container_groups.get(
            resource_group,
            resource.id.split("/")[-1],
        ).ip_address.ip
