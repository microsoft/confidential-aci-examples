import base64
import json
import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.http_request import request
from infra.test_case import TestCase


class KeyReleaseTest(TestCase):
    def test_status(self):
        assert self.container_ip is not None

        response = request(
            method="get",
            url=f"http://{self.container_ip}:8000/status",
        )
        assert response.status_code == 200, response.content.decode()
        assert json.loads(response.content.decode())["message"] == "Status OK"

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
                    "kid": f"{self.name}-key",
                }
            ),
        )
        assert response.status_code == 200, response.content.decode()
        assert json.loads(json.loads(response.content.decode())["key"])["k"] != ""

    # NOT CURRENTLY WORKING
    # def test_raw_attest(self):
    #     assert self.container_ip is not None

    #     response = request(
    #         method="post",
    #         url=f"http://{self.container_ip}:8000/attest/raw",
    #         headers={
    #             "Content-Type": "application/json",
    #         },
    #         data=json.dumps(
    #             {
    #                 "runtime_data": base64.urlsafe_b64encode(
    #                     "EXAMPLEREPORTDATA".encode()
    #                 ).decode(),
    #             }
    #         ),
    #     )
    #     assert response.status_code == 200, response.content.decode()
    #     assert json.loads(response.content.decode())["message"] != ""

    # def test_maa_attest(self):
    #     assert self.container_ip is not None

    #     response = request(
    #         method="post",
    #         url=f"http://{self.container_ip}:8000/attest/maa",
    #         headers={
    #             "Content-Type": "application/json",
    #         },
    #         data=json.dumps(
    #             {
    #                 "maa_endpoint": os.environ["AZURE_ATTESTATION_ENDPOINT"],
    #                 "runtime_data": base64.b64encode(
    #                     "EXAMPLEREPORTDATA".encode()
    #                 ).decode(),
    #             }
    #         ),
    #     )
    #     assert response.status_code == 200, response.content.decode()
    #     assert json.loads(response.content.decode())["token"] != ""


if __name__ == "__main__":
    unittest.main()
