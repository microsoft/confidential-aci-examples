import os
import subprocess


def update_policies():
    for dirpath, _, filenames in os.walk(
        os.path.join(os.path.dirname(__file__), "..", "tests")
    ):
        if "arm_template.json" in filenames:
            os.chdir(dirpath)
            subprocess.run(
                f"az confcom acipolicygen -a arm_template.json --save-to-file security_policy.rego",
                shell=True,
                check=True,
            )


if __name__ == "__main__":
    update_policies()
