import argparse
import json


def read_manifest_ports(manifest):
    ports = set()
    for container_group in manifest["containerGroups"]:
        ports.update(container_group["ports"])
    return ports


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read ports from a manifest")
    parser.add_argument("path", type=str, help="Path to manifest file")
    args = parser.parse_args()

    with open(args.path, "r") as manifest_file:
        manifest = json.load(manifest_file)
        print(read_manifest_ports(manifest))
