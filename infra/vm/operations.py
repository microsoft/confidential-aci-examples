# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import json
import os
import pexpect
import subprocess


def copy_to_vm(
    ip_address: str,
    user_password: str,
    src_path: str,
    dest_path: str,
):
    process = pexpect.spawn(
        f"scp -o StrictHostKeyChecking=no -r {src_path} test-user@{ip_address}:{dest_path}"
    )
    process.expect(f"test-user@{ip_address}'s password: ")
    process.sendline(user_password)
    process.expect(pexpect.EOF)
    print(process.before.decode("utf-8"))


def run_on_vm(
    vm_name: str,
    command: str,
):
    print(f"Running command '{command}'")
    command = f"{os.linesep}az vm run-command invoke -g $AZURE_RESOURCE_GROUP -n {vm_name} --command-id RunPowerShellScript --scripts '{command}'"
    raw_output = subprocess.check_output(command, shell=True)
    output = json.loads(raw_output.decode("utf-8"))["value"][0]["message"]
    print(output)
    return output
