import argparse
import json
import os
import sys
import tempfile
import subprocess

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.clients import get_blob_service_client
from infra.keys import generate_key_file, deploy_key


class CryptSetupFileSystem:
    DEVICE_NAME = "cryptdevice1"
    DEVICE_NAME_PATH = f"/dev/mapper/{DEVICE_NAME}"

    def _run_command(self, *args):
        subprocess.check_call(
            " ".join(
                [
                    "sudo cryptsetup --debug -v",
                    *args,
                ]
            ),
            shell=True,
        )

    def __init__(self, key_path, image_path):
        self.key_path = key_path
        self.image_path = image_path
        with open(image_path, "wb") as f:
            f.seek(64 * 1024 * 1024 - 1)
            f.write(b"\0")

    def __enter__(self):
        # Format
        self._run_command(
            "luksFormat",
            "--type luks2",
            self.image_path,
            "--key-file",
            f'"{self.key_path}"',
            "--batch-mode",
            "--sector-size 4096",
            "--cipher aes-xts-plain64",
            "--pbkdf pbkdf2",
            "--pbkdf-force-iterations 1000",
        )

        # Open
        self._run_command(
            "luksOpen",
            self.image_path,
            self.DEVICE_NAME,
            "--key-file",
            self.key_path,
            # Don't use a journal to increase performance
            "--integrity-no-journal",
            "--persistent",
        )

        # Mount
        subprocess.check_call(f"sudo mkfs.ext4 {self.DEVICE_NAME_PATH}", shell=True)
        self._dir = tempfile.TemporaryDirectory()
        subprocess.check_call(
            f"sudo mount -t ext4 {self.DEVICE_NAME_PATH} {self._dir.name} -o loop",
            shell=True,
        )
        return self._dir.name

    def __exit__(self, exc_type, exc_value, traceback):
        subprocess.check_call(f"sudo umount {self._dir.name}", shell=True)
        self._run_command("luksClose", self.DEVICE_NAME)
        self._dir.cleanup()


def deploy_blob(arm_template: dict, key_file_path: str):
    blob_name = arm_template["variables"]["uniqueId"] + "-blob"
    blob_service_client = get_blob_service_client(
        account_url=f"https://{os.environ['AZURE_STORAGE_ACCOUNT_NAME']}.blob.core.windows.net",
    )
    blob_client = blob_service_client.get_blob_client(
        container=os.environ["AZURE_STORAGE_CONTAINER_NAME"], blob=blob_name
    )

    if blob_client.exists():
        blob_client.delete_blob()

    with tempfile.TemporaryDirectory() as blob_dir:
        blob_path = os.path.join(blob_dir, blob_name)
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b"This is a file in the encrypted filesystem!")
        with CryptSetupFileSystem(key_file_path, blob_path) as filesystem:
            file_path = os.path.join(filesystem, "file.txt")
            subprocess.check_call(f"sudo cp {tmp_file.name} {file_path}", shell=True)
        with open(blob_path, mode="rb") as data:
            blob_client.upload_blob(data)

    print(f"Deployed blob {blob_name} into the storage container")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm-template-path", required=True)
    args = parser.parse_args()

    with open(
        args.arm_template_path, "r"
    ) as f, tempfile.NamedTemporaryFile() as tmp_key_file:
        arm_template = json.load(f)
        key = generate_key_file(tmp_key_file)
        # tmp_key_file.name will look something like '/tmp/tmptjujjt' -- the path to the file
        deploy_blob(arm_template, tmp_key_file.name)
        deploy_key(arm_template, key)
