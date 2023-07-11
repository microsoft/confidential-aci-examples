import argparse
import json
import subprocess


def login_arm_template_registries(arm_template):
    for registry_info in arm_template["resources"][0]["properties"][
        "imageRegistryCredentials"
    ]:
        registry, username, password = registry_info.values()
        print(f"Logging into {registry}")
        subprocess.run(
            f"docker login {registry} --username {username} --password {password}",
            shell=True,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Log into all registries in an ARM template")
    parser.add_argument(
        "--arm-template-path",
        help="The path to the ARM template to log into the registries of",
        required=True,
    )

    args = parser.parse_args()

    with open(args.arm_template_path, "r") as arm_template_file:
        arm_template = json.load(arm_template_file)
        login_arm_template_registries(arm_template)
