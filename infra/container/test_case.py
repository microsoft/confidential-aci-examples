import json
import os

from infra.build_and_push_images import build_and_push_images
from infra.add_security_policy_to_arm_template import (
    add_security_policy_to_arm_template,
)
from infra.clients import get_container_client, get_resource_client
from infra.deploy_arm_template import deploy_arm_template, run_pre_deploy_script
from infra.container.generate_arm_template import generate_arm_template
from infra.generate_security_policy import generate_security_policy
from infra.container.get_ip import get_container_ip
from infra.delete_deployment import delete_deployment


def setUpAci(cls):
    # Check if the deployment already exists
    get_container_ip_func = lambda: get_container_ip(
        resource_client=get_resource_client(os.environ["AZURE_SUBSCRIPTION_ID"]),
        container_client=get_container_client(os.environ["AZURE_SUBSCRIPTION_ID"]),
        resource_group=os.environ["AZURE_RESOURCE_GROUP"],
        deployment_name=cls.deployment_name,
    )

    cls.container_ip = get_container_ip_func()
    if cls.container_ip:
        return

    build_and_push_images(
        image_tag=cls.image_tag,
        manifest=cls.manifest,
    )

    # Deploy the container with the freshly built image
    arm_template_path = f"examples/{cls.test_name}/arm_template.json"
    arm_template = generate_arm_template(
        name=f"group-{cls.name}",
        image_tag=cls.image_tag,
        manifest=cls.manifest,
        location="eastus2euap",
        out=arm_template_path,
    )

    if os.getenv("SECURITY_POLICY") is None:
        security_policy = generate_security_policy(arm_template)
        with open(f"examples/{cls.test_name}/_generated.rego", "w") as f:
            f.write(security_policy.decode("utf-8"))
    else:
        with open(f"examples/{os.getenv('SECURITY_POLICY')}", "rb") as f:
            security_policy = f.read()

    if "preDeployScript" in cls.manifest:
        run_pre_deploy_script(cls.manifest, arm_template_path)

    deploy_arm_template(
        resource_client=get_resource_client(os.environ["AZURE_SUBSCRIPTION_ID"]),
        arm_template=add_security_policy_to_arm_template(
            arm_template=arm_template,
            security_policy=security_policy,
        ),
        resource_group=os.environ["AZURE_RESOURCE_GROUP"],
        deployment_name=cls.deployment_name,
    )

    cls.container_ip = get_container_ip_func()


def tearDownAci(cls):
    if os.getenv("CLEANUP_ACI") not in ["0", "false", "False"]:
        with open(f"examples/{cls.test_name}/arm_template.json", "r") as f:
            delete_deployment(
                resource_client=get_resource_client(
                    os.environ["AZURE_SUBSCRIPTION_ID"]
                ),
                resource_group=os.environ["AZURE_RESOURCE_GROUP"],
                deployment_name=cls.deployment_name,
                arm_template=json.load(f),
                asynchronous=True,
            )
