import subprocess
import json


def get_containerplat(directory_path: str):
    subprocess.run(
        f'az artifacts universal download --organization "https://dev.azure.com/msazure/" --project "dcf1de98-e135-4121-8a6c-99b73705f581" --scope project --feed "ContainerPlat-Dev" --name "containerplat-confidential-aci" --version "0.1.0-rc.3" --path "{directory_path}"',
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
