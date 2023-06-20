import argparse
import json
import os
import subprocess
import sys
from base64 import b64encode
import tempfile

import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.clients import get_network_client
from infra.vm.get_ip import get_vm_ip
from infra.vm.operations import copy_to_vm, run_on_vm


def run_containerplat(
    ip_address: str,
    user_password: str,
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
        ip_address,
        user_password,
        f"C:\ContainerPlat\crictl.exe pull --auth {b64encode(auth_string.encode('utf-8')).decode()} --pod-config C:\lcow_configs\lcow-pull-config.json {image}",
        timeout=600,
    )

    # Run the container
    pod_id = run_on_vm(
        ip_address,
        user_password,
        f"C:\ContainerPlat\crictl.exe runp --runtime runhcs-lcow C:\lcow_configs\pod.json",
    ).strip("\r\n")

    # Run the container
    container_id = run_on_vm(
        ip_address,
        user_password,
        f"C:\ContainerPlat\crictl.exe create --no-pull {pod_id} C:\lcow_configs\lcow-container.json C:\lcow_configs\pod.json",
    ).strip("\r\n")

    run_on_vm(
        ip_address,
        user_password,
        f"C:\ContainerPlat\crictl.exe start {container_id}",
    ).strip("\r\n")

    endpoints_json = run_on_vm(
        ip_address,
        user_password,
        f"hnsdiag list endpoints -df",
    )

    container_ip_address = json.loads(endpoints_json)["IPAddress"]

    with tempfile.TemporaryDirectory() as temp_dir:
        start_server_path = os.path.join(temp_dir, "start_server.ps1")
        with open(start_server_path, "w") as f:
            ports = "\n".join(
                [f"$listener.Prefixes.Add('http://*:{port}/')" for port in [8000, 8001]]
            )
            f.write(
                f"""
$listener = New-Object System.Net.HttpListener
{ports}
$listener.Start()

while ($listener.IsListening)
{{
    $context = $listener.GetContext()
    $requestUrl = $context.Request.Url
    $endpoint = $requestUrl.Segments[-1]
    $port = $requestUrl.Port
    $response = $context.Response

    echo "Received request for $($requestUrl.AbsoluteUri)"

    $passthroughCall = "http://{container_ip_address}:$port/$endpoint"
    $buffer = Invoke-WebRequest -Uri $passthroughCall -UseBasicParsing | Select-Object -ExpandProperty Content
    $bufferBytes = [System.Text.Encoding]::UTF8.GetBytes($buffer)
    $response.ContentLength64 = $bufferBytes.Length
    $response.OutputStream.Write($bufferBytes, 0, $bufferBytes.Length)
    $response.Close()
}}
            """
            )
        copy_to_vm(
            ip_address,
            user_password,
            start_server_path,
            "/start_server.ps1",
        )
        run_on_vm(
            ip_address,
            user_password,
            f"powershell -File C:\start_server.ps1",
            timeout=0,
        )

    subprocess.run(
        f"curl {ip_address}:8000/hello",
        shell=True,
    )

    return ip_address


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
                ip_address=vm_ip,
                user_password=arm_template["variables"]["vmPassword"],
                image=f"{os.getenv('AZURE_REGISTRY_URL')}/simple_server/primary:latest",
            )
        )
