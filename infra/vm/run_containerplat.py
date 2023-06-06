import argparse
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.clients import get_network_client
from infra.vm.get_ip import get_vm_ip
from infra.vm.operations import run_on_vm


def run_containerplat(
    ip_address: str,
    user_password: str,
    image: str,
) -> None:
    # Pull the container image
    run_on_vm(
        ip_address,
        user_password,
        f"C:\ContainerPlat\crictl.exe pull --pod-config C:\lcow_configs\lcow-pull-config.json {image}",
    )

    # Start the container group (pod)
    pod_id = run_on_vm(
        ip_address,
        user_password,
        "C:\ContainerPlat\crictl.exe runp --runtime runhcs-lcow C:\lcow_configs\pod.json",
    ).strip("\r\n")

    # Run the container
    run_on_vm(
        ip_address,
        user_password,
        f"C:\ContainerPlat\crictl.exe run --no-pull {pod_id} C:\lcow_configs\lcow-container.json C:\lcow_configs\pod.json",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm-template-path", required=True)
    args = parser.parse_args()

    with open(args.arm_template_path) as f:
        arm_template = json.load(f)
        run_containerplat(
            ip_address=get_vm_ip(
                network_client=get_network_client(os.environ["AZURE_SUBSCRIPTION_ID"]),
                resource_group=os.environ["AZURE_RESOURCE_GROUP"],
                ip_name=f'{arm_template["variables"]["uniqueId"]}-ip',
            ),
            user_password=arm_template["variables"]["vmPassword"],
            image="docker.io/library/alpine:latest",
        )
