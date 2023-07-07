import argparse
import json
import os
import runpy
import sys
import uuid
import runpy
from azure.mgmt.resource import ResourceManagementClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from infra.clients import get_resource_client


def run_pre_deploy_script(manifest: dict, arm_template_path: str):
    script_path = os.path.join(
        "examples",
        manifest["testName"],
        manifest["preDeployScript"],
    )
    sys.argv = [script_path] + ["--arm-template-path", arm_template_path]
    runpy.run_path(script_path, run_name="__main__")


def deploy_arm_template(
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
        "--manifest-path",
        help="The path to the manifest of the deployment",
        required=True,
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

    with open(args.arm_template_path) as arm_template_file:
        with open(args.manifest_path) as manifest_file:
            manifest = json.load(manifest_file)

            if "preDeployScript" in manifest:
                run_pre_deploy_script(manifest, args.arm_template_path)

            deploy_arm_template(
                resource_client=get_resource_client(
                    args.subscription_id or os.environ["AZURE_SUBSCRIPTION_ID"]
                ),
                arm_template=json.load(arm_template_file),
                resource_group=args.resource_group
                or os.environ["AZURE_RESOURCE_GROUP"],
                deployment_name=args.deployment_name or f"deployment-{uuid.uuid4()}",
            )
