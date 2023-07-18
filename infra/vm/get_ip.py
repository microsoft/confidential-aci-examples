import argparse
import os
from typing import Optional
from azure.mgmt.network import NetworkManagementClient


from infra.clients import get_network_client


def get_vm_ip(
    network_client: NetworkManagementClient,
    resource_group: str,
    ip_name: str,
) -> Optional[str]:
    try:
        ip_address = network_client.public_ip_addresses.get(
            resource_group_name=resource_group,
            public_ip_address_name=ip_name,
        ).ip_address

        print(f"{ip_address=}")
        return ip_address
    except Exception as e:
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip-name", required=True)
    args = parser.parse_args()

    print(
        get_vm_ip(
            network_client=get_network_client(os.environ["AZURE_SUBSCRIPTION_ID"]),
            resource_group=os.environ["AZURE_RESOURCE_GROUP"],
            ip_name=args.ip_name,
        )
    )
