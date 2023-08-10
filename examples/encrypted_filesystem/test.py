import unittest
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.http_request import request
from infra.test_case import TestCase


class EncryptedFilesystemTest(TestCase):
    def test_encfs_read(self):
        time.sleep(30)
        assert self.container_ip is not None
        response = request(f"http://{self.container_ip}:8000/read")
        assert response.status_code == 200, response.content.decode("utf-8")
        print(response.content.decode("utf-8"))
        assert (
            response.content.decode("utf-8").strip("\n")
            == "This is a file in the encrypted filesystem!"
        )

    def test_encfs_write(self):
        time.sleep(30)
        assert self.container_ip is not None

        response = request(f"http://{self.container_ip}:8000/write")
        assert response.status_code == 200, response.content.decode("utf-8")
        print(response.content.decode("utf-8"))
        assert response.content.decode("utf-8").strip("\n") == "This is a new file in the encrypted filesystem!"


if __name__ == "__main__":
    unittest.main()
