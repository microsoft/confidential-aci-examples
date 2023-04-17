import argparse
import json


def read_manifest_security_policies(manifest_path: str):
    with open(manifest_path, "r") as manifest_file:
        manifest = json.load(manifest_file)
    return manifest["security_policies"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Read security policy paths from a manifest"
    )
    parser.add_argument("path", type=str, help="Path to manifest file")
    args = parser.parse_args()
    print(read_manifest_security_policies(args.path))
