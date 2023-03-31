import os

SUBSCRIPTION_ID = os.getenv("AZ_SUBSCRIPTION_ID", "")
RESOURCE_GROUP = os.getenv("AZ_RESOURCE_GROUP", "")
REGISTRY_PASSWORD = os.getenv("AZ_REGISTRY_PASSWORD", "")


def set_credentials(
    subscription_id: str,
    resource_group: str,
    registry_password: str,
):
    credentials = {
        "AZ_SUBSCRIPTION_ID": subscription_id,
        "AZ_RESOURCE_GROUP": resource_group,
        "AZ_REGISTRY_PASSWORD": registry_password,
    }

    for key, value in credentials.items():
        os.environ[key] = value
        with open(f'{os.path.expanduser("~/.bashrc")}', "a") as f:
            f.write(f"\nexport {key}={value}")
        with open(
            f'{os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "env"))}',
            "a",
        ) as f:
            f.write(f"\n{key}={value}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--subscription-id",
        help="The subscription to deploy the ACI with.",
        required=True,
        type=str,
    )
    parser.add_argument(
        "--resource-group",
        help="The resource group to deploy the ACI with.",
        required=True,
        type=str,
    )
    parser.add_argument(
        "--registry-password",
        help="The password for the Azure Container Registry to publish images to.",
        required=True,
        type=str,
    )
    args = parser.parse_args()

    set_credentials(
        args.subscription_id,
        args.resource_group,
        args.registry_password,
    )
