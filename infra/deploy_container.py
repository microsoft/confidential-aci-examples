import argparse
import json
import os
import sys
from azure.mgmt.resource import ResourceManagementClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from infra.resource_client import get_resource_client


def deploy_container(
    resource_client: ResourceManagementClient,
    arm_template: dict,
    resource_group: str,
    name: str,
):
    resource_client.deployments.begin_create_or_update(
        resource_group,
        name,
        {
            "properties": {
                "template": arm_template,
                "parameters": {},
                "mode": "Incremental",
            }
        },  # type: ignore
    ).wait()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy Container on ACI")
    parser.add_argument(
        "--subscription-id",
        help="Subscription to deploy the container with",
        type=lambda x: x or os.getenv("AZ_SUBSCRIPTION_ID"),
    )
    parser.add_argument(
        "--arm-template-path",
        help="The path to the ARM template to use for deployment",
        required=True,
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

    args = parser.parse_args()

    with open(args.arm_template_path) as f:
        deploy_container(
            resource_client=get_resource_client(args.subscription_id),
            arm_template=json.load(f),
            resource_group=args.resource_group,
            name=args.container_name,
        )
