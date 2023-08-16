from contextlib import contextmanager
import os
import subprocess
import json
import tempfile
from typing import Optional
import zipfile
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.vm.build_hcsshim import build_hcsshim


@contextmanager
def update_package(package_path: str):
    with tempfile.TemporaryDirectory() as unzipped_dir:
        with zipfile.ZipFile(package_path, "a") as zip_ref:
            zip_ref.extractall(unzipped_dir)
            yield unzipped_dir
            for root, dirs, files in os.walk(unzipped_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zip_ref.write(file_path, os.path.relpath(file_path, unzipped_dir))


def get_containerplat(
    directory_path: str,
    hcsshim_url: Optional[str] = None,
):
    subprocess.run(
        f'az artifacts universal download --organization "https://dev.azure.com/msazure/" --project "dcf1de98-e135-4121-8a6c-99b73705f581" --scope project --feed "ContainerPlat-Prod" --name "containerplat-confidential-aci" --version "0.1.3" --path "{directory_path}"',
        shell=True,
    )

    with open(f"{directory_path}/deploy.json", "r+") as f:
        data = json.load(f)
        data["Force"] = True
        data["SevSnpEnabled"] = True
        data["EnableLayerIntegrity"] = True
        data["NoLCOWGPU"] = True
        data["RuntimeOptions"][0]["ShareScratch"] = True
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

    subprocess.run(
        f"cat {directory_path}/deploy.json | jq",
        shell=True,
    )

    if hcsshim_url is not None:
        build_hcsshim(
            package_path=f"{directory_path}/package.zip",
            hcsshim_url=hcsshim_url,
        )
