import argparse
from base64 import b64encode
import json
from typing import Any, Dict


def add_security_policy_to_arm_template(
    arm_template: Dict[str, Any],
    security_policy: bytes,
):
    arm_template["resources"][0]["properties"]["confidentialComputeProperties"][
        "ccePolicy"
    ] = b64encode(security_policy).decode("utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Add security policy to an ARM template"
    )
    parser.add_argument(
        "--arm-template-path",
        help="Path to the ARM template file",
        required=True,
    )
    parser.add_argument(
        "--security-policy-path",
        help="Path to the security policy file",
        required=True,
    )

    args = parser.parse_args()

    with open(args.arm_template_path) as f:
        arm_template = json.load(f)

    with open(args.security_policy_path, "rb") as f:
        security_policy = f.read()

    updated_arm_template = add_security_policy_to_arm_template(**vars())

    with open(args.arm_template_path, "w") as f:
        json.dump(updated_arm_template, f, indent=2)
