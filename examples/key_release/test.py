import json
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.http_request import request
from infra.test_case import TestCase


class KeyReleaseTest(TestCase):
    def test_key_release(self):
        assert self.container_ip is not None

        response = request(
            method="post",
            url=f"http://{self.container_ip}:8000/key/release",
            headers={
                "Content-Type": "application/json",
            },
            data=json.dumps(
                {
                    "maa_endpoint": os.environ["AZURE_ATTESTATION_ENDPOINT"],
                    "akv_endpoint": os.environ["AZURE_HSM_ENDPOINT"],
                    "kid": f"group-{self.name}-key",
                }
            ),
        )
        assert response.status_code == 200
        assert json.loads(json.loads(response.content.decode())["key"])["k"] != ""


if __name__ == "__main__":
    unittest.main()
