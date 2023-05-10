import argparse
import json
import os
import sys
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from infra.docker_client import get_docker_client


REGISTRY = "caciexamples.azurecr.io"


def build_and_push_images(image_tag: str, manifest: dict):
    client = get_docker_client(
        registry=REGISTRY,
        registry_password=os.getenv("AZ_REGISTRY_PASSWORD", ""),
    )
    for image_name, dockerfile_path in manifest["images"].items():
        repository = f"{manifest['testName']}/{image_name}"
        image_url = f"{REGISTRY}/{repository}"

        print(f"Building {repository}:{image_tag}")
        client.images.build(
            dockerfile=dockerfile_path,
            tag=f"{image_url}:{image_tag}",
            path=os.path.abspath("examples"),
        )

        print(f"Pushing {repository}:{image_tag}")
        client.images.push(f"{image_url}", tag=image_tag)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build and Push Images")
    parser.add_argument(
        "--image-tag",
        help="The tag to use for the iamges",
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
