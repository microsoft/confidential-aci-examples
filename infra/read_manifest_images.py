# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse
import json


def read_manifest_images(manifest):
    return [
        f"{repository}:{dockerfile}"
        for repository, dockerfile in manifest["images"].items()
    ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read images from a manifest")
    parser.add_argument("path", type=str, help="Path to manifest file")
    args = parser.parse_args()

    with open(args.path, "r") as manifest_file:
        manifest = json.load(manifest_file)
        print(read_manifest_images(manifest))
