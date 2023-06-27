import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.http_request import request
from infra.test_case import TestCase


class SimpleServerTest(TestCase):
    def test_endpoint(self):
        assert self.container_ip is not None

        response = request(f"http://{self.container_ip}:8000/hello")
        assert response.status_code == 200
        assert response.content.decode("utf-8").strip("\n") == "Hello world!"


if __name__ == "__main__":
    unittest.main()
