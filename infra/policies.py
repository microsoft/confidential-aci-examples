from base64 import b64encode
import json
import os
import subprocess
import tempfile


def generate_security_policy(arm_template_path: str, security_policy_path: str) -> None:
    subprocess.run(
        f"az confcom acipolicygen -a {arm_template_path} --outraw --save-to-file {security_policy_path}",
        shell=True,
        check=True,
    )


def template_to_security_policy(arm_template):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Emit the arm template to a temporary file
        arm_template_file = os.path.join(tmpdir, "arm_template.json")
        with open(arm_template_file, "w") as f:
            json.dump(arm_template, f, indent=2)

        # Generate the security policy
        security_policy_file = os.path.join(tmpdir, "security_policy.rego")
        generate_security_policy(
            arm_template_path=arm_template_file,
            security_policy_path=security_policy_file,
        )

        return b64encode(open(security_policy_file, "rb").read()).decode("utf-8")


def update_policies():
    for dirpath, _, filenames in os.walk(
        os.path.join(os.path.dirname(__file__), "..", "tests")
    ):
        if "arm_template.json" in filenames:
            generate_security_policy(
                arm_template_path=os.path.join(dirpath, "arm_template.json"),
                security_policy_path=os.path.join(dirpath, "security_policy.rego"),
            )


if __name__ == "__main__":
    update_policies()
