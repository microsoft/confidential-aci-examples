import unittest
import sys
import uuid
import requests
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

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


class SimpleServerTest(unittest.TestCase):
    def setUp(self):
        self.container_name = os.getenv(
            "CONTAINER_NAME", f"simple-server-{uuid.uuid4()}"
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
        repository = "simple_server"
        tag = "latest"
        client = get_docker_client(
            registry=registry,
            registry_password=os.getenv("AZ_REGISTRY_PASSWORD", ""),
        )
        client.images.build(
            dockerfile="Dockerfile",
            tag=tag,
            path=os.path.abspath("tests/simple_server"),
        )
        client.images.push(f"{registry}/{repository}", tag=tag)

        # Deploy the container with the freshly built image
        arm_template = generate_arm_template(
            name=self.container_name,
            image=f"{registry}/{repository}:{tag}",
            out="tests/simple_server/arm_template.json",
            registry_password=os.getenv("AZ_REGISTRY_PASSWORD", ""),
        )

        security_policy = generate_security_policy(arm_template)
        with open("tests/simple_server/security_policy.rego", "w") as f:
            f.write(security_policy.decode("utf-8"))

        deploy_container(
            resource_client=get_resource_client(os.getenv("AZ_SUBSCRIPTION_ID")),
            arm_template=add_security_policy_to_arm_template(
                arm_template=arm_template,
                security_policy=security_policy,
            ),
            resource_group=os.getenv("AZ_RESOURCE_GROUP", ""),
            name=self.container_name,
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

    def test_get_attestation(self):
        assert self.container_ip is not None
        response = requests.get(f"http://{self.container_ip}:8000/get_attestation")
        assert response.status_code == 200
        assert response.content == b"Getting attestation\n"


if __name__ == "__main__":
    unittest.main()
