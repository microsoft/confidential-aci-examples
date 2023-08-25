import os
import subprocess
import json
from typing import Optional
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.vm.build_hcsshim import build_hcsshim


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
