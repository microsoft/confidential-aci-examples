# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse
import json
import subprocess
import tempfile
import sys
import os
from git import Repo

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.keys import generate_key_file, deploy_key

def generate_wrapped_data(key):
    # get skr executable
    #subprocess.run("curl -L https://github.com/microsoft/confidential-sidecar-containers/releases/latest/download/skr > skr", stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, input="", shell=True)
    
    # temp method for testing
    Repo.clone_from("https://github.com/microsoft/confidential-sidecar-containers.git", "sidecars")

    subprocess.run("go build -o skr ./sidecars/cmd/skr/main.go", stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, input="", shell=True)

    with tempfile.NamedTemporaryFile() as f:
        f.write("Oceans are full of water\nHorses have 4 legs")
        
        subprocess.run(f"skr --infile plaintext --keypath {key} --outfile /examples/key_release/wrapped", stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, input="", shell=True)



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
        generate_wrapped_data(key)
