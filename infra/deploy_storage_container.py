import argparse
import os
import subprocess
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from infra.clients import get_blob_service_client


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--resource-group", default=os.environ["AZURE_RESOURCE_GROUP"])
    parser.add_argument("--location", required=True)
    parser.add_argument("--container-name", required=True)
    parser.add_argument(
        "--subscription-id",
        default=os.environ["AZURE_SUBSCRIPTION_ID"],
    )
    parser.add_argument(
        "--admin-ids",
        default=[
            os.environ["AZURE_SERVICE_PRINCIPAL_OBJECT_ID"],
            os.environ["AZURE_MANAGED_IDENTITY_ID"],
        ],
        nargs="+",
    )

    args = parser.parse_args()

    # Check if the storage account exists/name is available
    name_check = json.loads(subprocess.check_output(
        " ".join(
            [
                "az storage account check-name",
                f"--name {args.name}",
            ]
        ),
        shell=True,
    ).decode("utf-8"))

    if name_check["nameAvailable"] == True:
        # Deploy the storage account
        subprocess.check_call(
            " ".join(
                [
                    "az storage account create",
                    f"--name {args.name}",
                    f"--resource-group {args.resource_group}",
                    f"--location {args.location}",
                    "--sku Standard_RAGRS",
                    "--kind StorageV2",
                ]
            ),
            shell=True,
        )
    elif name_check["reason"] == "AccountNameInvalid":
        print(name_check["message"])
        sys.exit(1)

    # Create Storage account container
    account_url = "https://{}.blob.core.windows.net".format(args.name)
    blob_service_client = get_blob_service_client(account_url)

    # Check if container exists or name is available/valid
    try:
        container_client = blob_service_client.create_container(args.container_name)
    except Exception as e:
        print(e)
        sys.exit(1)

    # Add the roles to the container
    for user in args.admin_ids:
        # Storage Blob Data Reader if the filesystem is read-only, Storage Blob Data Contributor if it's read-write
        for role in ["Reader", "Storage Blob Data Contributor"]:
            subprocess.run(
                " ".join(
                    [
                        "az role assignment create",
                        f'--role "{role}"',
                        f"--assignee {user}",
                        f"--scope /subscriptions/{args.subscription_id}/resourcegroups/{args.resource_group}/providers/Microsoft.Storage/storageAccounts/{args.name}/blobServices/default/containers/{args.container_name}",
                    ]
                ),
                shell=True,
            )
