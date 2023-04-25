import struct
import unittest
import sys
import requests
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.aci_test_case import AciTestCase

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from get_attestation import SNP_REPORT_STRUCTURE


class AttestationTest(AciTestCase):
    def test_attestation_report(self):
        assert self.container_ip is not None

        input_report_data = "EXAMPLEREPORTDATA"
        response = requests.get(
            f"http://{self.container_ip}:8000/get_attestation?report_data={input_report_data}"
        )

        assert response.status_code == 200
        report = struct.unpack_from(f"<{SNP_REPORT_STRUCTURE}", response.content, 0)
        assert report[10].rstrip(b"\x00").decode() == input_report_data


if __name__ == "__main__":
    unittest.main()
