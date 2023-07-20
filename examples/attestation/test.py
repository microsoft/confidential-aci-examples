import struct
import unittest
import sys
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.http_request import request
from infra.test_case import TestCase

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from get_attestation import SNP_REPORT_STRUCTURE
from validate_attestation import validate_attestation


class AttestationTest(TestCase):
    def test_attestation_report(self):
        assert self.container_ip is not None

        input_report_data = "EXAMPLEREPORTDATA"
        response = request(
            f"http://{self.container_ip}:8000/get_attestation?report_data={input_report_data}",
        )

        assert response.status_code == 200
        report = struct.unpack_from(f"<{SNP_REPORT_STRUCTURE}", response.content, 0)
        assert report[10].rstrip(b"\x00").decode() == input_report_data

        response = request(
            f"http://{self.container_ip}:8000/get_attestation_from_sidecar?report_data={input_report_data}",
        )
        assert response.status_code == 200
        sidecar_report = struct.unpack_from(
            f"<{SNP_REPORT_STRUCTURE}", response.content, 0
        )
        assert sidecar_report == report

    def test_attestation_validation(self):
        assert self.container_ip is not None

        input_report_data = "EXAMPLEREPORTDATA"
        report_response = request(
            f"http://{self.container_ip}:8000/get_attestation?report_data={input_report_data}",
        )

        certificate_chain_response = request(
            f"http://{self.container_ip}:8000/get_certificate_chain",
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
