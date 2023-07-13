import argparse
from base64 import b64encode
import json
import os
import re


def resolve_manifest_variables(manifest: dict) -> dict:
    def clean_match(match):
        return match.group(0).replace("$", "").strip('"')

    manifest_str = json.dumps(manifest)
    evaluated_manifest = json.loads(
        re.sub(
            pattern='"\$(.*?)"',
            repl=lambda match: f'"{os.environ[clean_match(match)]}"',
            string=manifest_str,
        )
    )
    for container_group in evaluated_manifest["containerGroups"]:
        for container in container_group["containers"]:
            for key, value in container.get("env", {}).items():
                if isinstance(value, dict):
                    container["env"][key] = b64encode(
                        json.dumps(value).encode()
                    ).decode()

    return evaluated_manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Resolve environment variables in a manifest"
    )
    parser.add_argument("path", type=str, help="Path to manifest file")
    args = parser.parse_args()
    with open(args.path, "r") as manifest_file:
        print(json.dumps(resolve_manifest_variables(json.load(manifest_file))))
