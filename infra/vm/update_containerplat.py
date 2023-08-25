from contextlib import contextmanager
import os
import tempfile
import zipfile


@contextmanager
def update_package(package_path: str):
    with tempfile.TemporaryDirectory() as unzipped_dir:
        with zipfile.ZipFile(package_path, "a") as zip_ref:
            zip_ref.extractall(unzipped_dir)
            yield unzipped_dir
            for root, dirs, files in os.walk(unzipped_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zip_ref.write(file_path, os.path.relpath(file_path, unzipped_dir))
