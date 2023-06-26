import argparse
import json
import os
import sys
import tempfile
from base64 import b64encode
from typing import Iterable

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.clients import get_network_client
from infra.vm.get_containerplat import get_containerplat
from infra.vm.get_ip import get_vm_ip
from infra.vm.operations import copy_to_vm, run_on_vm


def deploy_containerplat(
    ip_address: str,
    container_plat_path: str,
    user_password: str,
    vm_name: str,
    image: str,
    security_policy: str,
    ports: Iterable[int] = [],
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
                    "linux": {"security_context": {"privileged": True}},
                    "annotations": {
                        "io.microsoft.virtualmachine.computetopology.processor.count": "2",
                        "io.microsoft.virtualmachine.computetopology.memory.sizeinmb": "8192",
                        "io.microsoft.virtualmachine.lcow.securitypolicy": security_policy,
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
                    "linux": {"security_context": {"privileged": True}},
                    "forwardPorts": ports,
                },
                f,
            )

        copy_to_vm(ip_address, user_password, temp_dir, "/lcow_configs")

    copy_to_vm(
        ip_address,
        user_password,
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "passthrough_server.ps1"
        ),
        "/passthrough_server.ps1",
    )

    # Deploy Containerplat
    run_on_vm(
        vm_name,
        "C:\\container_plat_build\\deploy.exe",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm-template-path", required=True)
    args = parser.parse_args()

    with open(args.arm_template_path) as f:
        with open(
            "examples/simple_server/security_policies/allow_all.rego"
        ) as policy_file:  # TODO: Use real security policy
            arm_template = json.load(f)
            security_policy = policy_file.read()

            vm_ip = get_vm_ip(
                network_client=get_network_client(os.environ["AZURE_SUBSCRIPTION_ID"]),
                resource_group=os.environ["AZURE_RESOURCE_GROUP"],
                ip_name=f'{arm_template["variables"]["uniqueId"]}-ip',
            )
            assert vm_ip

            with tempfile.TemporaryDirectory() as temp_dir:
                get_containerplat(temp_dir)
                deploy_containerplat(
                    ip_address=vm_ip,
                    container_plat_path=temp_dir,
                    user_password=arm_template["variables"]["vmPassword"],
                    vm_name=f'{arm_template["variables"]["uniqueId"]}-vm',
                    image=f"{os.getenv('AZURE_REGISTRY_URL')}/simple_server/primary:latest",
                    security_policy=b64encode(security_policy.encode("utf-8")).decode(),
                    ports=arm_template["variables"]["containerPorts"],
                )
