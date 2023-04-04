import docker
from functools import lru_cache


@lru_cache
def get_docker_client(
    registry: str,
    registry_password: str,
) -> docker.DockerClient:
    client = docker.from_env()
    client.login(
        registry=registry,
        username=registry.split(".")[0],
        password=registry_password,
    )
    return client
