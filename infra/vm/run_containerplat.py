import argparse
import json
import os
import sys
from base64 import b64encode
from typing import Iterable

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.clients import get_network_client
from infra.vm.get_ip import get_vm_ip
from infra.vm.operations import copy_to_vm, run_on_vm


def run_containerplat(
    vm_name: str,
    ports: Iterable[int],
    image: str,
) -> str:
    # Pull the container image
    auth_string = ":".join(
        [
            os.environ["AZURE_REGISTRY_USERNAME"],
            os.environ["AZURE_REGISTRY_PASSWORD"],
        ]
    )
    run_on_vm(
        vm_name,
        f"C:\ContainerPlat\crictl.exe pull --auth {b64encode(auth_string.encode('utf-8')).decode()} --pod-config C:\lcow_configs\lcow-pull-config.json {image}",
    )

    # Run the container
    pod_id = run_on_vm(
        vm_name,
        f"C:\ContainerPlat\crictl.exe runp --runtime runhcs-lcow C:\lcow_configs\pod.json",
    ).strip("\r\n")

    # Run the container
    container_id = run_on_vm(
        vm_name,
        f"C:\ContainerPlat\crictl.exe create --no-pull {pod_id} C:\lcow_configs\lcow-container.json C:\lcow_configs\pod.json",
    ).strip("\r\n")

    run_on_vm(
        vm_name,
        f"C:\ContainerPlat\crictl.exe start {container_id}",
    ).strip("\r\n")

    endpoints_json = run_on_vm(
        vm_name,
        f"hnsdiag list endpoints -df",
    )

    return json.loads(endpoints_json)["IPAddress"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm-template-path", required=True)
    args = parser.parse_args()

    with open(args.arm_template_path) as f:
        arm_template = json.load(f)

        vm_ip = get_vm_ip(
            network_client=get_network_client(os.environ["AZURE_SUBSCRIPTION_ID"]),
            resource_group=os.environ["AZURE_RESOURCE_GROUP"],
            ip_name=f'{arm_template["variables"]["uniqueId"]}-ip',
        )
        assert vm_ip

        print(
            run_containerplat(
                vm_name=f'{arm_template["variables"]["uniqueId"]}-vm',
                ports=arm_template["variables"]["containerPorts"],
                image=f"{os.getenv('AZURE_REGISTRY_URL')}/simple_server/primary:latest",
            )
        )
