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
        deployment = resource_client.deployments.get(
            resource_group,
            deployment_name,
        )
        assert deployment.properties.output_resources
    except Exception as e:
        print(e)
        return

    for resource in deployment.properties.output_resources:
        return container_client.container_groups.get(
            resource_group,
            resource.id.split("/")[-1],
        ).ip_address.ip
