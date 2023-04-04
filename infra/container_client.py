from functools import lru_cache
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.identity import DefaultAzureCredential


@lru_cache
def get_container_client(subscription_id: str) -> ContainerInstanceManagementClient:
    return ContainerInstanceManagementClient(DefaultAzureCredential(), subscription_id)
