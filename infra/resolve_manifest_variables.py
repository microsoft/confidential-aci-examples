import argparse
import os
import re


def resolve_manifest_variables(manifest_path: str):
    def clean_match(match):
        return match.group(0).replace("$", "").strip('"')

    with open(manifest_path, "r") as manifest_file:
        manifest_str = manifest_file.read()
        return re.sub(
            pattern='"\$(.*)"',
            repl=lambda match: f'"{os.environ[clean_match(match)]}"',
            string=manifest_str,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Resolve environment variables in a manifest"
    )
    parser.add_argument("path", type=str, help="Path to manifest file")
    args = parser.parse_args()
    print(resolve_manifest_variables(args.path))
