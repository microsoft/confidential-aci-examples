import argparse
import os
from typing import Iterable
import docker
from credentials import REGISTRY_PASSWORD

# Set up the Docker client
client = docker.from_env()


def build_docker_image(payload: str, tag: str) -> docker.models.images.Image:
    # Build the Docker image with the file path mounted onto it
    image, build_logs = client.images.build(
        dockerfile="infra/Dockerfile",
        tag=tag,
        path=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
        buildargs={"payload": payload},
    )

    # Print the logs from the build process
    for line in build_logs:
        print(line.get("stream", "").strip())

    # Print the ID of the new image
    print(f"Built new image with ID {image.id}")

    # Return the Docker image object
    return image


def publish_docker_image(
    image: docker.models.images.Image,
    registry: str,
    registry_password: str,
    repository: str,
    tag: str,
) -> None:
    # Authenticate with the container registry
    client.login(
        registry=registry,
        username=registry.split(".")[0],
        password=registry_password,
    )

    image.tag(f"{registry}/{repository}", tag=tag)

    # Push the Docker image to the container registry
    for line in client.images.push(
        f"{registry}/{repository}",
        tag=tag,
        stream=True,
    ):
        print(line.decode().strip())


if __name__ == "__main__":
    # Define the command-line arguments
    parser = argparse.ArgumentParser(
        description="Build and publish a Docker image with a file mounted onto it"
    )
    parser.add_argument("file_path", help="The path to the file to be mounted")
    parser.add_argument(
        "--tag", help="The tag to use for the Docker image", required=True
    )
    parser.add_argument(
        "--registry", help="The container registry to publish the image to"
    )
    parser.add_argument("--repository", help="The repository name for the image")
    parser.add_argument(
        "--push-tag", default="latest", help="The tag for the published image"
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    # Build the Docker image with the provided file path
    image = build_docker_image(args.file_path, tag=args.tag)

    # If a container registry is specified, publish the Docker image to that registry
    if args.registry and args.repository:
        publish_docker_image(
            image,
            args.registry,
            REGISTRY_PASSWORD,
            args.repository,
            tag=args.push_tag,
        )
