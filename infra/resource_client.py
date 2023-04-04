from functools import lru_cache
from azure.mgmt.resource import ResourceManagementClient
from azure.identity import DefaultAzureCredential


@lru_cache
def get_resource_client(subscription_id: str) -> ResourceManagementClient:
    return ResourceManagementClient(DefaultAzureCredential(), subscription_id)
