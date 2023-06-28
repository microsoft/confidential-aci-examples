import json
import multiprocessing
import os
import tempfile
import uuid
from infra.build_and_push_images import build_and_push_images
from infra.clients import get_network_client, get_resource_client
from infra.delete_deployment import delete_deployment
from infra.deploy_arm_template import deploy_arm_template
from infra.vm.deploy_containerplat import deploy_containerplat
from infra.vm.generate_arm_template import generate_arm_template
from infra.vm.get_containerplat import get_containerplat
from infra.vm.get_ip import get_vm_ip
from infra.vm.passthrough_server import run_passthrough_server
from infra.vm.run_containerplat import run_containerplat
from base64 import b64encode


def setUpVm(cls):
    build_and_push_images(
        image_tag=cls.image_tag,
        manifest=cls.manifest,
    )

    vm_user_password = str(uuid.uuid4())

    for idx, container_group in enumerate(cls.manifest["containerGroups"]):
        get_vm_ip_func = lambda: get_vm_ip(
            network_client=get_network_client(os.environ["AZURE_SUBSCRIPTION_ID"]),
            resource_group=os.environ["AZURE_RESOURCE_GROUP"],
            ip_name=f"{cls.name}-{idx}-ip",
        )

        vm_ip = get_vm_ip_func()
        if vm_ip:
            return

        arm_template = generate_arm_template(
            name=f"{cls.name}-{idx}",
            password=vm_user_password,
            location="eastus",
            manifest=cls.manifest,
            out=f"examples/{cls.test_name}/arm_template.json",
        )

        deploy_arm_template(
            resource_client=get_resource_client(os.environ["AZURE_SUBSCRIPTION_ID"]),
            manifest=cls.manifest,
            arm_template=arm_template,
            resource_group=os.environ["AZURE_RESOURCE_GROUP"],
            deployment_name=f"{cls.deployment_name}-{idx}",
        )

        vm_ip = get_vm_ip_func()
        assert vm_ip

        # TODO: Support multiple containers
        assert len(container_group["containers"]) == 1

        # TODO: User generated security policy
        with open(
            "examples/simple_server/security_policies/allow_all.rego"
        ) as policy_file:
            security_policy = policy_file.read()

        for container in container_group["containers"]:
            image = f"{os.getenv('AZURE_REGISTRY_URL')}/{cls.manifest['testName']}/{container['image']}:{cls.image_tag}"

            with tempfile.TemporaryDirectory() as temp_dir:
                get_containerplat(temp_dir)

                deploy_containerplat(
                    ip_address=vm_ip,
                    container_plat_path=temp_dir,
                    user_password=vm_user_password,
                    vm_name=f'{arm_template["variables"]["uniqueId"]}-vm',
                    image=image,
                    security_policy=b64encode(security_policy.encode("utf-8")).decode(),
                )

                container_ip_address = run_containerplat(
                    vm_name=f'{arm_template["variables"]["uniqueId"]}-vm',
                    image=image,
                    ports=arm_template["variables"]["containerPorts"],
                )

                cls.passthrough_server = multiprocessing.Process(
                    target=run_passthrough_server,
                    kwargs={
                        "vm_name": f'{arm_template["variables"]["uniqueId"]}-vm',
                        "ports": {8000},
                        "ip_address": container_ip_address,
                    },
                )
                cls.passthrough_server.start()

                cls.container_ip = "localhost"


def tearDownVm(cls):
    cls.passthrough_server.terminate()
    with open(f"examples/{cls.test_name}/arm_template.json", "r") as f:
        for idx, _ in enumerate(cls.manifest["containerGroups"]):
            delete_deployment(
                resource_client=get_resource_client(
                    os.environ["AZURE_SUBSCRIPTION_ID"]
                ),
                resource_group=os.environ["AZURE_RESOURCE_GROUP"],
                deployment_name=f"{cls.deployment_name}-{idx}",
                arm_template=json.load(f),
                asynchronous=True,
            )
