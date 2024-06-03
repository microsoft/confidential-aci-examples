# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse
import json
import os
import sys
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from infra.clients import get_docker_client


def build_and_push_images(image_tag: str, manifest: dict):
    registry = os.environ["AZURE_REGISTRY_URL"]
    client = get_docker_client(
        registry=registry,
        registry_password=os.environ["AZURE_REGISTRY_PASSWORD"],
    )
    for image_name, dockerfile_path in manifest["images"].items():
        repository = f"{manifest['testName']}/{image_name}"
        image_url = f"{registry}/{repository}"

        print(f"Building {repository}:{image_tag}")
        client.images.build(
            dockerfile=dockerfile_path,
            tag=f"{image_url}:{image_tag}",
            path=os.path.abspath("examples"),
            buildargs={
                "RUN_ID": image_tag, 
                "AZURE_HSM_ENDPOINT": os.environ["AZURE_HSM_ENDPOINT"], 
                "AZURE_ATTESTATION_ENDPOINT": os.environ["AZURE_ATTESTATION_ENDPOINT"],
                "AZURE_SERVICE_PRINCIPAL_APP_ID": os.environ["AZURE_SERVICE_PRINCIPAL_APP_ID"],
                "AZURE_SERVICE_PRINCIPAL_PASSWORD": os.environ["AZURE_SERVICE_PRINCIPAL_PASSWORD"],
                "AZURE_SERVICE_PRINCIPAL_TENANT": os.environ["AZURE_SERVICE_PRINCIPAL_TENANT"]
            }
        )

        print(f"Pushing {repository}:{image_tag}")
        client.images.push(f"{image_url}", tag=image_tag)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build and Push Images")
    parser.add_argument(
        "--image-tag",
        help="The tag to use for the images",
        type=str,
    )
    parser.add_argument(
        "--manifest-path",
        help="The path to the manifest file describing images to build and push",
        required=True,
    )
    args = parser.parse_args()

    with open(args.manifest_path, "r") as manifest_file:
        build_and_push_images(
            image_tag=args.image_tag or str(uuid.uuid4()),
            manifest=json.load(manifest_file),
        )
