import base64
import binascii
import hashlib
import json
import struct
import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from examples.attestation.get_attestation import SNP_REPORT_STRUCTURE
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

    def test_raw_attest(selAddf):
        assert self.container_ip is not None

        input_report_data = b"EXAMPLEREPORTDATA"
        response = request(
            method="post",
            url=f"http://{self.container_ip}:8000/attest/raw",
            headers={
                "Content-Type": "application/json",
            },
            data=json.dumps(
                {
                    "runtime_data": base64.urlsafe_b64encode(
                        input_report_data
                    ).decode(),
                }
            ),
        )
        assert response.status_code == 200, response.content.decode()
        report_str = json.loads(response.content.decode())["report"]

        # Report data isn't returned as Hex, so we unhex around it
        skr_report = struct.unpack_from(
            f"<{SNP_REPORT_STRUCTURE}",
            (
                binascii.unhexlify(report_str[:160])
                + report_str[160:224].encode()  # Report Data
                + binascii.unhexlify(report_str[224:])
            ),
            0,
        )

        # SKR Sidecar decodes the base64 string and then hashes it before
        # providing it to the SNP Attestation
        assert (
            skr_report[10].rstrip(b"\x00").decode()
            == hashlib.sha256(input_report_data).hexdigest()
        )

    def test_maa_attest(self):
        assert self.container_ip is not None

        # MAA expects report data in a particular format
        input_report_data = json.dumps(
            {
                "keys": [
                    {
                        "key_ops": ["encrypt"],
                        "kid": "test-key",
                        "kty": "oct-HSM",
                        "k": "example",
                    }
                ]
            }
        )

        response = request(
            method="post",
            url=f"http://{self.container_ip}:8000/attest/maa",
            headers={
                "Content-Type": "application/json",
            },
            data=json.dumps(
                {
                    "maa_endpoint": os.environ["AZURE_ATTESTATION_ENDPOINT"],
                    "runtime_data": base64.urlsafe_b64encode(
                        input_report_data.encode()
                    ).decode(),
                }
            ),
        )
        assert response.status_code == 200, response.content.decode()
        assert json.loads(response.content.decode())["token"] != ""


if __name__ == "__main__":
    unittest.main()
