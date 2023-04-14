import os
import re
import unittest
import uuid
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from infra.add_security_policy_to_arm_template import (
    add_security_policy_to_arm_template,
)
from infra.container_client import get_container_client
from infra.deploy_container import deploy_container
from infra.docker_client import get_docker_client
from infra.generate_arm_template import generate_arm_template
from infra.generate_security_policy import generate_security_policy
from infra.get_container_ip import get_container_ip
from infra.remove_container import remove_container
from infra.resource_client import get_resource_client


class AciTestCase(unittest.TestCase):
    def setUp(self):
        test_name = self.__class__.__name__.replace("Test", "")
        snake_case_test_name = re.sub(r"(?<!^)(?=[A-Z])", "_", test_name).lower()
        dash_case_test_name = re.sub(r"(?<!^)(?=[A-Z])", "-", test_name).lower()

        self.container_name = os.getenv(
            "DEPLOYMENT_NAME", f"{dash_case_test_name}-{uuid.uuid4()}"
        )

        # Check if the container already exists
        get_container_ip_func = lambda: get_container_ip(
            resource_client=get_resource_client(os.getenv("AZ_SUBSCRIPTION_ID")),
            container_client=get_container_client(os.getenv("AZ_SUBSCRIPTION_ID")),
            resource_group=os.getenv("AZ_RESOURCE_GROUP", ""),
            name=self.container_name,
        )

        self.container_ip = get_container_ip_func()
        if self.container_ip:
            return

        # If the container doesn't exist, deploy it, starting by building and
        # pushing the image
        registry = "caciexamples.azurecr.io"
        repository = snake_case_test_name
        tag = "latest"
        client = get_docker_client(
            registry=registry,
            registry_password=os.getenv("AZ_REGISTRY_PASSWORD", ""),
        )
        client.images.build(
            dockerfile="Dockerfile",
            tag=tag,
            path=os.path.abspath(f"tests/{snake_case_test_name}"),
        )
        client.images.push(f"{registry}/{repository}", tag=tag)

        # Deploy the container with the freshly built image
        arm_template = generate_arm_template(
            container_group_name=self.container_name,
            image=f"{registry}/{repository}:{tag}",
            location="eastus2euap",
            out=f"tests/{snake_case_test_name}/arm_template.json",
            registry_password=os.getenv("AZ_REGISTRY_PASSWORD", ""),
        )

        security_policy = generate_security_policy(arm_template)
        with open(f"tests/{snake_case_test_name}/security_policy.rego", "w") as f:
            f.write(security_policy.decode("utf-8"))

        deploy_container(
            resource_client=get_resource_client(os.getenv("AZ_SUBSCRIPTION_ID")),
            arm_template=add_security_policy_to_arm_template(
                arm_template=arm_template,
                security_policy=security_policy,
            ),
            resource_group=os.getenv("AZ_RESOURCE_GROUP", ""),
            deployment_name=self.container_name,
        )

        self.container_ip = get_container_ip_func()

    def tearDown(self):
        if os.getenv("CLEANUP_ACI") not in ["0", "false", "False"]:
            remove_container(
                resource_client=get_resource_client(os.getenv("AZ_SUBSCRIPTION_ID")),
                container_client=get_container_client(os.getenv("AZ_SUBSCRIPTION_ID")),
                resource_group=os.getenv("AZ_RESOURCE_GROUP", ""),
                name=self.container_name,
                asynchronous=True,
            )
