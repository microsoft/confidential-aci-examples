# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

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
        f"C:\ContainerPlat