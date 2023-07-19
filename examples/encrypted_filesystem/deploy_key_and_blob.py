import argparse
from base64 import b64encode, b64decode
import binascii
import hashlib
import json
import os
import sys
import tempfile
import subprocess
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.clients import get_blob_service_client

KEY_FILE_PATH = "keyfile.bin"


def deploy_key(arm_template: dict, key: bytes):
    name = arm_template["variables"]["uniqueId"]

    resources = arm_template["resources"]
    assert len(resources) == 1

    security_policy_digest = hashlib.sha256(
        b64decode(
            resources[0]["properties"]["confidentialComputeProperties"]["ccePolicy"]
        )
    ).hexdigest()

    response = requests.put(
        url=f"https://{os.environ['AZURE_HSM_ENDPOINT']}/keys/{name}-key?api-version=7.3-preview",
        data=json.dumps(
            {
                "key": {
                    "kty": "oct-HSM",
                    "k": key.decode(),
                    "key_size": 256,
                },
                "hsm": True,
                "attributes": {
                    "exportable": True,
                },
                "release_policy": {
                    "contentType": "application/json; charset=utf-8",
                    "data": b64encode(
                        json.dumps(
                            {
                                "version": "0.2",
                                "anyOf": [
                                    {
                                        "authority": f"https://{os.environ['AZURE_ATTESTATION_ENDPOINT']}",
                                        "allOf": [
                                            {
                                                "claim": "x-ms-sevsnpvm-hostdata",
                                                "equals": security_policy_digest,
                                            },
                                            {
                                                "claim": "x-ms-compliance-status",
                                                "equals": "azure-compliant-uvm",
                                            },
                                            {
                                                "claim": "x-ms-sevsnpvm-is-debuggable",
                                                "equals": "false",
                                            },
                                        ],
                                    }
                                ],
                            }
                        ).encode()
                    ).decode(),
                    "immutable": False,
                },
            }
        ),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer "
            + json.loads(
                subprocess.check_output(
                    "az account get-access-token --resource https://managedhsm.azure.net",
                    shell=True,
                )
            )["accessToken"],
        },
    )

    assert response.status_code == 200, response.content
    print(f"Deployed key {name}-key into the HSM")


# cryptsetupCommand runs cryptsetup with the provided arguments
def cryptsetup_command(args: list[str]):
	# --debug and -v are used to increase the information printed by
	# cryptsetup. By default, it doesn't print much information, which makes it
	# hard to debug it when there are problems.
    cmd = ["sudo cryptsetup --debug -v"] + args
    subprocess.check_call(
        " ".join(cmd),
        shell=True,
    )


def cryptsetup_format(image_name: str):
    args = ["luksFormat", "--type luks2", image_name,
    "--key-file", KEY_FILE_PATH, "--batch-mode", "--sector-size 4096",
    "--cipher aes-xts-plain64",
    "--pbkdf pbkdf2", "--pbkdf-force-iterations 1000"]

    cryptsetup_command(args)


# cryptsetupOpen runs "cryptsetup luksOpen" with the right arguments.
def cryptsetup_open(image_name: str, device_name: str):
	args = [ "luksOpen", image_name, device_name, "--key-file", KEY_FILE_PATH,
		# Don't use a journal to increase performance
		"--integrity-no-journal",
		"--persistent"]

	cryptsetup_command(args)


def cryptsetup_close(device_name: str):
    args = ["luksClose", device_name]
    cryptsetup_command(args)


def generate_blob(name: str):
    encrypted_image = name
    device_name = "cryptdevice1"
    device_name_path = f"/dev/mapper/{device_name}"

    # create folder to copy into filesystem
    local_fs_name = "filesystem"
    local_file_path = os.path.join(local_fs_name, "file.txt")
    os.makedirs(local_fs_name,exist_ok=True)
    with open(local_file_path, 'w') as f:
        f.write("This is a file in the encrypted filesystem!")

    print("Creating encrypted image ", encrypted_image)
    subprocess.check_call(
        " ".join(
            [
                f"rm -f {encrypted_image};",
                f"touch {encrypted_image};",
                f"truncate --size 64M {encrypted_image}",
            ]
        ),
        shell=True,
    )

    cryptsetup_format(encrypted_image)
    cryptsetup_open(encrypted_image, device_name)

    try:
        print("[!] Formatting as ext4...")
        subprocess.check_call(f"sudo mkfs.ext4 {device_name_path}", shell=True)

        print("[!] Mounting...")
        with tempfile.TemporaryDirectory() as mount_point:
            subprocess.check_call(f"sudo mount -t ext4 {device_name_path} {mount_point} -o loop", shell=True)

            print("[!] Copying contents to encrypted device...")

            # The /* is needed to copy folder contents instead of the folder + contents
            subprocess.check_call(f"sudo cp -r filesystem/* {mount_point}", shell=True)
            subprocess.check_call(f"ls {mount_point}", shell=True)

            print("[!] Closing device...")
            subprocess.check_call(f"sudo umount {mount_point}", shell=True)
    finally:
        cryptsetup_close(device_name)

    # clean up local filesystem and encrypted image
    os.remove(local_file_path)
    os.rmdir(local_fs_name)
    os.remove(encrypted_image)


def deploy_blob(arm_template: dict):
    name = arm_template["variables"]["uniqueId"] + "-blob"

    # generate encrypted blob
    generate_blob(name)

    # Deploy the container
    account_url = f"https://{os.environ['AZURE_STORAGE_ACCOUNT_NAME']}.blob.core.windows.net"
    blob_service_client = get_blob_service_client(account_url)
    blob_client = blob_service_client.get_blob_client(container=os.environ['AZURE_STORAGE_CONTAINER_NAME'], blob=name)

    with open(file=name, mode="rb") as data:
        blob_client.upload_blob(data)
    
    print(f"Deployed blob {name} into the storage container")


def generate_key_file():
    if not os.path.exists(KEY_FILE_PATH):
        print("Generating key file")
        subprocess.check_call(f"dd if=/dev/random of={KEY_FILE_PATH} count=1 bs=32", shell=True)

    print("Getting key in hex string format")
    bFile = open(KEY_FILE_PATH,'rb')
    bData = bFile.read(32)

    subprocess.check_call(f"truncate -s 32 {KEY_FILE_PATH}", shell=True)
    return binascii.hexlify(bData)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm-template-path", required=True)
    args = parser.parse_args()

    key = generate_key_file()

    with open(args.arm_template_path, "r") as f:
        deploy_blob(json.load(f))
        deploy_key(json.load(f), key)

    # remove local key file
    os.remove(KEY_FILE_PATH)
