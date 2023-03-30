import argparse
import os
import docker

# Set up the Docker client
client = docker.from_env()


def build_docker_image(docker_file_path: str, tag: str) -> docker.models.images.Image:
    # Build the Docker image with the file path mounted onto it
    image, build_logs = client.images.build(
        dockerfile="Dockerfile",
        tag=tag,
        path=os.path.abspath(os.path.dirname(docker_file_path)),
    )

    # Print the logs from the build process
    for line in build_logs:
        print(line.get("stream", "").strip())

    # Print the ID of the new image
    print(f"Built new image with ID {image.id}")

    # Return the Docker image object
    return image


def image_exists(
    registry: str,
    registry_password: str,
    image_url: str,
) -> bool:
    try:
        client.login(
            registry=registry,
            username=registry.split(".")[0],
            password=registry_password,
        )
        client.images.get(image_url)
        return True
    except docker.errors.ImageNotFound:
        return False


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

    print(f"Pushed image to {registry}/{repository}:{tag}")


if __name__ == "__main__":
    # Define the command-line arguments
    parser = argparse.ArgumentParser(
        description="Build and publish a Docker image with a file mounted onto it"
    )

    parser.add_argument(
        "docker_file_path",
        help="The path to the dockerfile to build the image with",
    )
    parser.add_argument(
        "--tag",
        help="The tag to use for the Docker image",
        required=True,
    )
    parser.add_argument(
        "--registry",
        help="The container registry to publish the image to",
    )
    parser.add_argument(
        "--registry-password",
        help="The password to the registry to push images to (Leave blank to use environment).",
        type=lambda pswd: pswd if pswd != "" else os.getenv("AZ_REGISTRY_PASSWORD"),
    )
    parser.add_argument(
        "--repository",
        help="The repository name for the image",
    )
    parser.add_argument(
        "--push-tag",
        default="latest",
        help="The tag for the published image",
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    # Build the Docker image with the provided file path
    image = build_docker_image(
        docker_file_path=args.docker_file_path,
        tag=args.tag,
    )

    # If a container registry is specified, publish the Docker image to that registry
    if args.registry and args.repository:
        publish_docker_image(
            image,
            args.registry,
            args.registry_password,
            args.repository,
            tag=args.push_tag,
        )
