import json
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

        self.instance_id = str(uuid.uuid4())
        self.container_name = os.getenv(
            "DEPLOYMENT_NAME", f"{dash_case_test_name}-{self.instance_id}"
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
        with open(f"tests/{snake_case_test_name}/manifest.json", "r") as manifest_file:
            manifest = json.load(manifest_file)
        registry = "caciexamples.azurecr.io"
        repository = manifest["testName"]
        tag = self.instance_id
        client = get_docker_client(
            registry=registry,
            registry_password=os.getenv("AZ_REGISTRY_PASSWORD", ""),
        )
        for image, dockerfile_path in manifest["images"].items():
            client.images.build(
                dockerfile=dockerfile_path,
                tag=f"{registry}/{repository}/{image}:{tag}",
                path=os.path.abspath("tests"),
            )
            client.images.push(f"{registry}/{repository}/{image}", tag=tag)

        # Deploy the container with the freshly built image
        arm_template = generate_arm_template(
            id=self.instance_id,
            name=self.instance_id,
            manifest=manifest,
            location="eastus2euap",
            out=f"tests/{snake_case_test_name}/arm_template.json",
        )

        security_policy = generate_security_policy(arm_template)
        with open(f"tests/{snake_case_test_name}/_generated.rego", "w") as f:
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
