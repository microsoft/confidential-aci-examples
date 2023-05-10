import unittest
import sys
import requests
import os
from requests.adapters import HTTPAdapter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.test_case import TestCase


class SimpleSidecarTest(TestCase):
    def test_sidecar_connection(self):
        assert self.container_ip is not None
        session = requests.Session()
        session.mount("http://", HTTPAdapter(max_retries=60))
        response = session.get(
            f"http://{self.container_ip}:8000/check_connection", timeout=20
        )
        assert response.status_code == 200
        assert response.content == b"True"


if __name__ == "__main__":
    unittest.main()
