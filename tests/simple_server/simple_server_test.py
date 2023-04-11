import unittest
import sys
import uuid
import requests
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.aci_test_case import AciTestCase


class SimpleServerTest(AciTestCase):
    def test_get_attestation(self):
        assert self.container_ip is not None
        response = requests.get(f"http://{self.container_ip}:8000/get_attestation")
        assert response.status_code == 200
        assert response.content == b"Getting attestation\n"


if __name__ == "__main__":
    unittest.main()
