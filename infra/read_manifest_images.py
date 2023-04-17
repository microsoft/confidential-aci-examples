import argparse
import json


def read_manifest_images(manifest_path: str):
    with open(manifest_path, "r") as manifest_file:
        manifest = json.load(manifest_file)
    return [f"{dockerfile}:{tag}" for dockerfile, tag in manifest["images"].items()]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read images from a manifest")
    parser.add_argument("path", type=str, help="Path to manifest file")
    args = parser.parse_args()
    print(read_manifest_images(args.path))
