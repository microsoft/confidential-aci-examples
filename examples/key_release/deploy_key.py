# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse
import json
import tempfile
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.keys import generate_key_file, deploy_key

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm-template-path", required=True)
    args = parser.parse_args()

    with open(
        args.arm_template_path, "r"
    ) as f, tempfile.NamedTemporaryFile() as tmp_key_file:
        key = generate_key_file(tmp_key_file)
        arm_template = json.load(f)
        deploy_key(arm_template["variables"]["uniqueId"] + "-key", arm_template, key)
