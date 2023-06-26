import unittest
import sys
import requests
import os
from requests.adapters import HTTPAdapter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.test_case import TestCase


class SimpleServerTest(TestCase):
    def test_endpoint(self):
        session = requests.Session()
        session.mount("http://", HTTPAdapter(max_retries=60))
        assert self.container_ip is not None
        response = session.get(f"http://{self.container_ip}:8000/hello", timeout=1000)
        assert response.status_code == 200
        assert response.content.decode("utf-8").strip("\n") == "Hello world!"


if __name__ == "__main__":
    unittest.main()
