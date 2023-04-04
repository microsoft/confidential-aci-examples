import json
import os
import subprocess
import tempfile
from typing import Any, Dict


def generate_security_policy(
    arm_template: Dict[str, Any],
) -> bytes:
    with tempfile.TemporaryDirectory() as tmp_dir:
        arm_template_path = os.path.join(tmp_dir, "arm_template.json")
        security_policy_path = os.path.join(tmp_dir, "security_policy.rego")

        with open(arm_template_path, "w") as f:
            json.dump(arm_template, f, indent=2)

        subprocess.run(
            f"az confcom acipolicygen -a {arm_template_path} --outraw --save-to-file {security_policy_path}",
            shell=True,
            check=True,
        )

        with open(security_policy_path, "rb") as f:
            return f.read()
