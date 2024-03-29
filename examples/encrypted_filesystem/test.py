# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.http_request import request
from infra.test_case import TestCase


class EncryptedFilesystemTestRW(TestCase):
    def test_encfs_rw_read(self):
        assert self.container_ip is not None

        response = request(f"http://{self.container_ip}:8000/read_rw_fs")
        assert response.status_code == 200, response.content.decode("utf-8")
        assert (
            response.content.decode("utf-8").strip("\n")
            == "This is a file in the encrypted filesystem!"
        )

    def test_encfs_rw_write(self):
        assert self.container_ip is not None

        response = request(f"http://{self.container_ip}:8000/write_rw_fs")
        assert response.status_code == 200, response.content.decode("utf-8")
        assert (
            response.content.decode("utf-8").strip("\n")
            == "This is a new file in the encrypted filesystem!"
        )


class EncryptedFilesystemTestRO(TestCase):
    def test_encfs_ro_read(self):
        assert self.container_ip is not None

        response = request(f"http://{self.container_ip}:8000/read_ro_fs")
        assert response.status_code == 200, response.content.decode("utf-8")
        assert (
            response.content.decode("utf-8").strip("\n")
            == "This is a file in the encrypted filesystem!"
        )

    def test_encfs_ro_write(self):
        assert self.container_ip is not None

        response = request(f"http://{self.container_ip}:8000/write_ro_fs")
        assert response.status_code == 400, response.content.decode("utf-8")
        assert (
            response.content.decode("utf-8").strip("\n")
            == "[Errno 30] Read-only file system: '/mnt/remote/share2/new_file.txt'"
        )


if __name__ == "__main__":
    unittest.main()
