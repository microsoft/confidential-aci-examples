import argparse
import json
import os
import subprocess
import tempfile
from typing import Any, Dict
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from infra.login_arm_template_registries import login_arm_template_registries
from infra.add_security_policy_to_arm_template import (
    add_security_policy_to_arm_template,
)


def generate_security_policy(
    arm_template: Dict[str, Any],
) -> bytes:
    print("Logging into Azure CLI")
    subprocess.run(
        "az login --service-principal --username $AZURE_SERVICE_PRINCIPAL_APP_ID --password $AZURE_SERVICE_PRINCIPAL_PASSWORD --tenant $AZURE_SERVICE_PRINCIPAL_TENANT",
        shell=True,
    )

    login_arm_template_registries(arm_template)

    with tempfile.TemporaryDirectory() as tmp_dir:
        arm_template_path = os.path.join(tmp_dir, "arm_template.json")
        security_policy_path = os.path.join(tmp_dir, "security_policy.rego")

        with open(arm_template_path, "w") as f:
            json.dump(arm_template, f, indent=2)

        subprocess.run(
            f"az confcom acipolicygen -a {arm_template_path} --outraw > {security_policy_path}",
            shell=True,
            check=True,
        )

        with open(security_policy_path, "rb") as f:
            return f.read()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Security Policy")
    parser.add_argument(
        "--arm-template-path",
        help="The path to the ARM template to generate the security policy from",
        required=True,
    )
    parser.add_argument(
        "--out",
        help="Path to save the security policy to",
    )

    args = parser.parse_args()

    with open(args.arm_template_path, "r") as arm_template_file:
        arm_template = json.load(arm_template_file)

    print(f"Generating Security Policy for ARM template {args.arm_template_path}")
    security_policy = generate_security_policy(
        arm_template=arm_template,
    )
    print("Done")

    print("Adding generated Security Policy to ARM template")
    with open(args.arm_template_path, "w") as arm_template_file:
        json.dump(
            add_security_policy_to_arm_template(
                arm_template=arm_template,
                security_policy=security_policy,
            ),
            arm_template_file,
            indent=2,
        )
    print("Done")

    if args.out:
        print(f"Saving Security Policy to {args.out}")
        with open(args.out, "wb") as f:
            f.write(security_policy)
        print("Done")
