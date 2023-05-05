import argparse
import json
import os
import sys
import uuid
from azure.mgmt.resource import ResourceManagementClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from infra.resource_client import get_resource_client


def deploy_container(
    resource_client: ResourceManagementClient,
    arm_template: dict,
    resource_group: str,
    deployment_name: str,
):
    print(f"Deploying {deployment_name} with resources:")
    for resource in arm_template["resources"]:
        print(f"    {resource['type'].split('/')[-1]} - {resource['name']}")
    resource_client.deployments.begin_create_or_update(
        resource_group,
        deployment_name,
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
    )
    parser.add_argument(
        "--arm-template-path",
        help="The path to the ARM template to use for deployment",
        required=True,
    )
    parser.add_argument(
        "--resource-group",
        help="The resource group to deploy the container with",
    )
    parser.add_argument(
        "--deployment-name",
        help="The name of the container deployment",
    )

    args = parser.parse_args()

    with open(args.arm_template_path) as f:
        deploy_container(
            resource_client=get_resource_client(
                args.subscription_id or os.getenv("AZ_SUBSCRIPTION_ID")
            ),
            arm_template=json.load(f),
            resource_group=args.resource_group or os.getenv("AZ_RESOURCE_GROUP", ""),
            deployment_name=args.deployment_name or f"deployment-{uuid.uuid4()}",
        )
