import struct
import unittest
import sys
import requests
import os
from requests.adapters import HTTPAdapter


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.test_case import TestCase

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from get_attestation import SNP_REPORT_STRUCTURE
from validate_attestation import validate_attestation


class AttestationTest(TestCase):
    def test_attestation_report(self):
        assert self.container_ip is not None

        input_report_data = "EXAMPLEREPORTDATA"
        session = requests.Session()
        session.mount("http://", HTTPAdapter(max_retries=60))
        response = session.get(
            f"http://{self.container_ip}:8000/get_attestation?report_data={input_report_data}",
            timeout=20,
        )

        assert response.status_code == 200
        report = struct.unpack_from(f"<{SNP_REPORT_STRUCTURE}", response.content, 0)
        assert report[10].rstrip(b"\x00").decode() == input_report_data

    def test_attestation_validation(self):
        assert self.container_ip is not None

        input_report_data = "EXAMPLEREPORTDATA"
        session = requests.Session()
        session.mount("http://", HTTPAdapter(max_retries=60))
        report_response = session.get(
            f"http://{self.container_ip}:8000/get_attestation?report_data={input_report_data}",
            timeout=20,
        )

        certificate_chain_response = session.get(
            f"http://{self.container_ip}:8000/get_certificate_chain",
            timeout=20,
        )

        assert report_response.status_code == 200
        assert certificate_chain_response.status_code == 200
        assert validate_attestation(
            report_response.content,
            certificate_chain_response.content,
            input_report_data,
        )


if __name__ == "__main__":
    unittest.main()
