import argparse
import os
import sys
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.containerinstance import ContainerInstanceManagementClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from infra.resource_client import get_resource_client
from infra.container_client import get_container_client


def remove_container(
    resource_client: ResourceManagementClient,
    container_client: ContainerInstanceManagementClient,
    resource_group: str,
    name: str,
    asynchronous: bool = False,
):
    try:
        deployment = resource_client.deployments.get(
            resource_group,
            name,
        )
    except Exception:
        print("Deployment not found")
        return

    if (
        deployment.properties is not None
        and deployment.properties.output_resources is not None
    ):
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy Container on ACI")
    parser.add_argument(
        "--subscription-id",
        help="Subscription to deploy the container with",
        type=lambda x: x or os.getenv("AZ_SUBSCRIPTION_ID"),
    )
    parser.add_argument(
        "--resource-group",
        help="The resource group to deploy the container with",
        type=lambda x: x or os.getenv("AZ_RESOURCE_GROUP"),
    )
    parser.add_argument(
        "--container-name",
        help="The name of the container to deploy",
        required=True,
    )
    parser.add_argument(
        "--asynchronous",
        help="Whether to remove the deployment asynchronously",
        action="store_true",
    )

    args = parser.parse_args()

    remove_container(
        resource_client=get_resource_client(args.subscription_id),
        container_client=get_container_client(args.subscription_id),
        resource_group=args.resource_group,
        name=args.container_name,
        asynchronous=args.asynchronous,
    )
