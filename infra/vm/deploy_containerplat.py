import argparse
import json
import os
import sys
import tempfile
import pexpect

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.clients import get_network_client
from infra.vm.get_containerplat import get_containerplat
from infra.vm.get_ip import get_vm_ip


def deploy_containerplat(
    ip_address: str,
    container_plat_path: str,
    user_password: str,
) -> None:
    # Attempt to send containerplat to VM
    command = f"scp -o StrictHostKeyChecking=no -r {os.path.abspath(container_plat_path)} test-user@{ip_address}:/container_plat_build"
    print(command)
    process = pexpect.spawn(command)

    # Expect password prompt
    process.expect(f"test-user@{ip_address}'s password: ")
    process.sendline(user_password)

    # Print the output
    process.expect(pexpect.EOF)
    print(process.before.decode("utf-8"))

    # Deploy containerplat
    process = pexpect.spawn(
        "ssh test-user@{ip_address} 'C:\\container_plat_build\\deploy.exe''"
    )
    process.expect(f"test-user@{ip_address}'s password: ")
    process.sendline(user_password)


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
            )
