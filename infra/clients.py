import docker

from functools import lru_cache
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


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


@lru_cache
def get_container_client(subscription_id: str) -> ContainerInstanceManagementClient:
    return ContainerInstanceManagementClient(DefaultAzureCredential(), subscription_id)


@lru_cache
def get_network_client(subscription_id: str) -> NetworkManagementClient:
    return NetworkManagementClient(DefaultAzureCredential(), subscription_id)


@lru_cache
def get_resource_client(subscription_id: str) -> ResourceManagementClient:
    return ResourceManagementClient(DefaultAzureCredential(), subscription_id)


@lru_cache
def get_blob_service_client(account_url: str) -> BlobServiceClient:
    return BlobServiceClient(account_url, DefaultAzureCredential())
