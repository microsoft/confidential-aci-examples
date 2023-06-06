import argparse
import json
import os
import sys
import tempfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.clients import get_network_client
from infra.vm.get_containerplat import get_containerplat
from infra.vm.get_ip import get_vm_ip
from infra.vm.operations import copy_to_vm, run_on_vm


def deploy_containerplat(
    ip_address: str,
    container_plat_path: str,
    user_password: str,
    image: str,
) -> None:
    copy_to_vm(
        ip_address,
        user_password,
        os.path.abspath(container_plat_path),
        "/container_plat_build",
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, "lcow-pull-config.json"), "w") as f:
            json.dump({"labels": {"sandbox-platform": "linux/amd64"}}, f)
        with open(os.path.join(temp_dir, "pod.json"), "w") as f:
            json.dump(
                {
                    "metadata": {
                        "name": "sandbox",
                        "namespace": "default",
                        "attempt": 1,
                    },
                    "annotations": {
                        "io.microsoft.virtualmachine.computetopology.processor.count": "4",
                        "io.microsoft.virtualmachine.computetopology.memory.sizeinmb": "16384",
                        "io.microsoft.virtualmachine.lcow.preferredrootfstype": "initrd",
                        "io.microsoft.virtualmachine.lcow.preferredrootfstype": "initrd",
                    },
                },
                f,
            )
        with open(os.path.join(temp_dir, "lcow-container.json"), "w") as f:
            json.dump(
                {
                    "metadata": {"name": "examples"},
                    "image": {"image": image},
                    "linux": {},
                },
                f,
            )

        copy_to_vm(ip_address, user_password, temp_dir, "/lcow_configs")

    # Deploy Containerplat
    run_on_vm(
        ip_address,
        user_password,
        "C:\container_plat_build\deploy.exe",
        timeout=600,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm-template-path", required=True)
    args = parser.parse_args()

    with open(args.arm_template_path) as f:
        arm_template = json.load(f)
        with tempfile.TemporaryDirectory() as temp_dir:
            get_containerplat(temp_dir)
            deploy_containerplat(
                ip_address=get_vm_ip(
                    network_client=get_network_client(
                        os.environ["AZURE_SUBSCRIPTION_ID"]
                    ),
                    resource_group=os.environ["AZURE_RESOURCE_GROUP"],
                    ip_name=f'{arm_template["variables"]["uniqueId"]}-ip',
                ),
                container_plat_path=temp_dir,
                user_password=arm_template["variables"]["vmPassword"],
                image="docker.io/library/alpine:latest",
            )
