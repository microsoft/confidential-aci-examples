import os

SUBSCRIPTION_ID = os.getenv("AZ_SUBSCRIPTION_ID")
RESOURCE_GROUP = os.getenv("AZ_RESOURCE_GROUP")
USERNAME = os.getenv("GH_USERNAME")
PAT = os.getenv("GH_PAT")


def set_credentials(subscription_id: str, resource_group: str, username: str, pat: str):
    credentials = {
        "AZ_SUBSCRIPTION_ID": subscription_id,
        "AZ_RESOURCE_GROUP": resource_group,
        "GH_USERNAME": username,
        "GH_PAT": pat,
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
        "--username",
        help="The username to authenticate with, needed while this repo is private.",
        type=str,
    )
    parser.add_argument(
        "--pat",
        help="The personal access token for the specified user, needed while this repo is private.",
        type=str,
    )
    args = parser.parse_args()

    set_credentials(args.subscription_id, args.resource_group, args.username, args.pat)
