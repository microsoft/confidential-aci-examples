import json
import os
import uuid

from infra.build_and_push_images import build_and_push_images
from infra.add_security_policy_to_arm_template import (
    add_security_policy_to_arm_template,
)
from infra.container_client import get_container_client
from infra.deploy_container import deploy_container
from infra.generate_arm_template import generate_arm_template
from infra.generate_security_policy import generate_security_policy
from infra.get_container_ip import get_container_ip
from infra.remove_container import remove_container
from infra.resource_client import get_resource_client


def setUpAci(cls):
    test_name = cls.__class__.__module__.split(".")[0]
    image_tag = str(uuid.uuid4())
    name = str(uuid.uuid4())

    with open(f"examples/{test_name}/manifest.json", "r") as manifest_file:
        manifest = json.load(manifest_file)

    cls.deployment_name = os.getenv("DEPLOYMENT_NAME", f"deployment-{name}")

    # Check if the container already exists
    get_container_ip_func = lambda: get_container_ip(
        resource_client=get_resource_client(os.getenv("AZ_SUBSCRIPTION_ID")),
        container_client=get_container_client(os.getenv("AZ_SUBSCRIPTION_ID")),
        resource_group=os.getenv("AZ_RESOURCE_GROUP", ""),
        deployment_name=cls.deployment_name,
    )

    cls.container_ip = get_container_ip_func()
    if cls.container_ip:
        return

    build_and_push_images(
        image_tag=image_tag,
        manifest=manifest,
    )

    # Deploy the container with the freshly built image
    arm_template = generate_arm_template(
        name=f"group-{name}",
        image_tag=image_tag,
        manifest=manifest,
        location="eastus2euap",
        out=f"examples/{test_name}/arm_template.json",
    )

    if os.getenv("SECURITY_POLICY") is None:
        security_policy = generate_security_policy(arm_template)
        with open(f"examples/{test_name}/_generated.rego", "w") as f:
            f.write(security_policy.decode("utf-8"))
    else:
        with open(f"examples/{os.getenv('SECURITY_POLICY')}", "rb") as f:
            security_policy = f.read()

    deploy_container(
        resource_client=get_resource_client(os.getenv("AZ_SUBSCRIPTION_ID")),
        arm_template=add_security_policy_to_arm_template(
            arm_template=arm_template,
            security_policy=security_policy,
        ),
        resource_group=os.getenv("AZ_RESOURCE_GROUP", ""),
        deployment_name=cls.deployment_name,
    )

    cls.container_ip = get_container_ip_func()


def tearDownAci(cls):
    if os.getenv("CLEANUP_ACI") not in ["0", "false", "False"]:
        remove_container(
            resource_client=get_resource_client(os.getenv("AZ_SUBSCRIPTION_ID")),
            container_client=get_container_client(os.getenv("AZ_SUBSCRIPTION_ID")),
            resource_group=os.getenv("AZ_RESOURCE_GROUP", ""),
            deployment_name=cls.deployment_name,
            asynchronous=True,
        )
