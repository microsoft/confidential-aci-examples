import unittest
import sys
import requests
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
print(f"Adding path: {ROOT_DIR}")
sys.path.insert(0, ROOT_DIR)

from infra import credentials
from infra.images import build_docker_image, image_exists, publish_docker_image
from infra.containers import (
    deploy_aci,
    get_aci_ip,
    remove_aci,
    get_resource_client,
    get_container_client,
)


class SimpleServerTest(unittest.TestCase):
    def setUp(self):
        registry = "caciexamples.azurecr.io"
        repository = "simple_server"
        tag = "latest"
        image_url = f"{registry}/{repository}:{tag}"
        if not image_exists(registry, credentials.REGISTRY_PASSWORD, image_url):
            publish_docker_image(
                image=build_docker_image(
                    docker_file_path="tests/simple_server/Dockerfile",
                    tag="simple_server",
                ),
                registry=registry,
                registry_password=credentials.REGISTRY_PASSWORD,
                repository=repository,
                tag=tag,
            )

        self.aci_name = "simple-server-test"  # TODO: Avoid clashing names
        get_aci_ip_func = lambda: get_aci_ip(
            resource_client=get_resource_client(credentials.SUBSCRIPTION_ID),
            container_client=get_container_client(credentials.SUBSCRIPTION_ID),
            resource_group=credentials.RESOURCE_GROUP,
            name=self.aci_name,
        )

        self.aci_ip = get_aci_ip_func()
        if self.aci_ip is None:
            deploy_aci(
                resource_client=get_resource_client(credentials.SUBSCRIPTION_ID),
                resource_group=credentials.RESOURCE_GROUP,
                name=self.aci_name,
                image=image_url,
                registry_password=credentials.REGISTRY_PASSWORD,
                arm_out="tests/simple_server/arm_template.json",
            )
            self.aci_ip = get_aci_ip_func()

    def tearDown(self):
        if os.getenv("CLEANUP_ACI") not in ["0", "false", "False"]:
            remove_aci(
                resource_client=get_resource_client(credentials.SUBSCRIPTION_ID),
                container_client=get_container_client(credentials.SUBSCRIPTION_ID),
                resource_group=credentials.RESOURCE_GROUP,
                name=self.aci_name,
                asynchronous=True,
            )

    def test_get_attestation(self):
        response = requests.get(f"http://{self.aci_ip}:8000/get_attestation")
        assert response.status_code == 200
        assert response.content == b"Getting attestation\n"


if __name__ == "__main__":
    unittest.main()
