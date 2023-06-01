import subprocess


def get_containerplat(directory_path: str):
    subprocess.run(
        f'az artifacts universal download --organization "https://dev.azure.com/msazure/" --project "dcf1de98-e135-4121-8a6c-99b73705f581" --scope project --feed "ContainerPlat-Prod" --name "containerplat-internal" --version "0.0.122" --path "{directory_path}"',
        shell=True,
    )
