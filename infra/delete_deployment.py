import argparse
import json
import os
import sys
from typing import Optional
from azure.mgmt.resource import ResourceManagementClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from infra.resource_client import get_resource_client


def delete_deployment(
    resource_client: ResourceManagementClient,
    resource_group: str,
    deployment_name: str,
    arm_template: Optional[dict],
    asynchronous: bool = False,
):
    try:
        deployment = resource_client.deployments.get(
            resource_group,
            deployment_name,
        )
    except Exception:
        print("Deployment not found")
        return

    if (
        deployment.properties is not None
        and deployment.properties.output_resources is not None
    ):
        for resource in deployment.properties.output_resources:
            arm_template_resource = next(
                res
                for res in arm_template["resources"]
                if res["name"] == resource.id.split("/")[-1]
            )
            delete_op = resource_client.resources.begin_delete_by_id(
                resource.id,
                arm_template_resource["apiVersion"],
            )
            if not asynchronous:
                delete_op.wait()

    delete_op = resource_client.deployments.begin_delete(
        resource_group, deployment_name
    )
    if not asynchronous:
        delete_op.wait()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy Container on ACI")
    parser.add_argument(
        "--subscription-id",
        help="Subscription to deploy the container with",
    )
    parser.add_argument(
        "--resource-group",
        help="The resource group to deploy the container with",
    )
    parser.add_argument(
        "--deployment-name",
        help="The name of the deployment to remove",
        required=True,
    )
    parser.add_argument(
        "--arm-template-path",
        help="The path to the ARM template used to deploy",
    )
    parser.add_argument(
        "--asynchronous",
        help="Whether to remove the deployment asynchronously",
        action="store_true",
    )

    args = parser.parse_args()

    arm_template = None
    if args.arm_template_path:
        with open(args.arm_template_path, "r") as arm_template_file:
            arm_template = json.load(arm_template_file)

    delete_deployment(
        resource_client=get_resource_client(
            args.subscription_id or os.getenv("AZ_SUBSCRIPTION_ID", "")
        ),
        resource_group=args.resource_group or os.getenv("AZ_RESOURCE_GROUP", ""),
        deployment_name=args.deployment_name,
        arm_template=arm_template,
        asynchronous=args.asynchronous,
    )
