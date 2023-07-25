import argparse
import json
import os
import sys
import tempfile
import subprocess

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.clients import get_blob_service_client
from infra.keys import generate_key_file, deploy_key


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


def cryptsetup_format(image_name: str, key_file_path: str):
    args = ["luksFormat", "--type luks2", image_name,
    "--key-file", key_file_path, "--batch-mode", "--sector-size 4096",
    "--cipher aes-xts-plain64",
    "--pbkdf pbkdf2", "--pbkdf-force-iterations 1000"]

    cryptsetup_command(args)


# cryptsetupOpen runs "cryptsetup luksOpen" with the right arguments.
def cryptsetup_open(image_name: str, device_name: str, key_file_path: str):
	args = [ "luksOpen", image_name, device_name, "--key-file", key_file_path,
		# Don't use a journal to increase performance
		"--integrity-no-journal",
		"--persistent"]

	cryptsetup_command(args)


def cryptsetup_close(device_name: str):
    args = ["luksClose", device_name]
    cryptsetup_command(args)


def generate_blob(name: str, key_file_path: str):
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

    cryptsetup_format(encrypted_image, key_file_path)
    cryptsetup_open(encrypted_image, device_name, key_file_path)

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


def deploy_blob(arm_template: dict, key_file_path: str):
    name = arm_template["variables"]["uniqueId"] + "-blob"

    # generate encrypted blob
    generate_blob(name, key_file_path)

    # Deploy the container
    account_url = f"https://{os.environ['AZURE_STORAGE_ACCOUNT_NAME']}.blob.core.windows.net"
    blob_service_client = get_blob_service_client(account_url)
    blob_client = blob_service_client.get_blob_client(container=os.environ['AZURE_STORAGE_CONTAINER_NAME'], blob=name)

    with open(file=name, mode="rb") as data:
        blob_client.upload_blob(data)
    
    print(f"Deployed blob {name} into the storage container")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm-template-path", required=True)
    args = parser.parse_args()

    with open(args.arm_template_path, "r") as f, tempfile.NamedTemporaryFile() as tmp_key_file:
        key = generate_key_file(tmp_key_file)
        # tmp_key_file.name will look something like '/tmp/tmptjujjt' -- the path to the file
        deploy_blob(json.load(f), tmp_key_file.name)
        deploy_key(json.load(f), key)
