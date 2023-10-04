# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse
from base64 import b64encode
import json
import os
import re


def resolve_manifest_variables(manifest: dict) -> dict:
    manifest = json.loads(os.path.expandvars(json.dumps(manifest)))
    for container_group in manifest["containerGroups"]:
        for container in container_group["containers"]:
            for key, value in container.get("env", {}).items():
                if isinstance(value, dict):
                    json_str = json.dumps(value)
                    if "$" not in json_str:
                        container["env"][key] = b64encode(json_str.encode()).decode()

    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Resolve environment variables in a manifest"
    )
    parser.add_argument("path", type=str, help="Path to manifest file")
    args = parser.parse_args()
    with open(args.path, "r") as manifest_file:
        print(json.dumps(resolve_manifest_variables(json.load(manifest_file))))
