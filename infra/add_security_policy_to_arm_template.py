import argparse
from base64 import b64encode
import json
from typing import Any, Dict


def add_security_policy_to_arm_template(
    arm_template: Dict[str, Any],
    security_policy: bytes,
):
    # ACI policygen returns concactenated policies for each group
    container_groups = [
        resource
        for resource in arm_template["resources"]
        if resource["type"] == "Microsoft.ContainerInstance/containerGroups"
    ]
    policies = [
        "package" + policy for policy in security_policy.decode().split("package")[1:]
    ]

    assert len(container_groups) == len(
        policies
    ), "Number of container groups does not match number of policies"

    for container_group, policy in zip(container_groups, policies):
        container_group["properties"]["confidentialComputeProperties"][
            "ccePolicy"
        ] = b64encode(policy.encode()).decode("utf-8")

    return arm_template


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

    updated_arm_template = add_security_policy_to_arm_template(
        arm_template=arm_template,
        security_policy=security_policy,
    )

    with open(args.arm_template_path, "w") as f:
        json.dump(updated_arm_template, f, indent=2)
