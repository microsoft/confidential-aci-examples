import json
import os
import uuid

from infra.build_and_push_images import build_and_push_images
from infra.add_security_policy_to_arm_template import (
    add_security_policy_to_arm_template,
)
from infra.clients import get_container_client, get_resource_client
from infra.deploy_arm_template import deploy_arm_template
from infra.container.generate_arm_template import generate_arm_template
from infra.generate_security_policy import generate_security_policy
from infra.container.get_ip import get_container_ip
from infra.delete_deployment import delete_deployment


def setUpAci(cls):
    test_name = cls.__class__.__module__.split(".")[0]
    image_tag = str(uuid.uuid4())
    name = str(uuid.uuid4())

    with open(f"examples/{test_name}/manifest.json", "r") as manifest_file:
        manifest = json.load(manifest_file)

    cls.deployment_name = os.getenv("DEPLOYMENT_NAME", f"deployment-{name}")

    # Check if the container already exists
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
        test_name = cls.__class__.__module__.split(".")[0]
        with open(f"examples/{test_name}/arm_template.json", "r") as f:
            delete_deployment(
                resource_client=get_resource_client(
                    os.environ["AZURE_SUBSCRIPTION_ID"]
                ),
                resource_group=os.environ["AZURE_RESOURCE_GROUP"],
                deployment_name=cls.deployment_name,
                arm_template=json.load(f),
                asynchronous=True,
            )
