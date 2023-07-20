import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.http_request import request
from infra.test_case import TestCase


class EncryptedFilesystemTest(TestCase):
    def test_encfs_deployment_succeeded(self):
        assert self.container_ip is not None

    def test_encfs_read(self):
        response = request(f"http://{self.container_ip}:8000/read")
        assert response.status_code == 200
        assert response.content.decode("utf-8").strip("\n") == "This is a file in the encrypted filesystem!"

    # can't do the write test until the public encfs image is updated
    # def test_encfs_write(self):
    #     assert self.container_ip is not None

    #     response = request(f"http://{self.container_ip}:8000/write")
    #     assert response.status_code == 200
    #     assert response.content.decode("utf-8").strip("\n") == "This is a new file in the encrypted filesystem!"

    def test_maa_token_acquired(self):
        response = request(f"http://{self.container_ip}:8000/maa_token")
        assert response.status_code == 200
        # searches that 'retrieving MAA token from MAA endpoint failed' not in log file
        # can search that 'MAA Token:' in log file instead
        assert response.content.decode("utf-8").strip("\n") == "Did not find text in file"


    def test_snp_report_acquired(self):
        response = request(f"http://{self.container_ip}:8000/snp_report")
        assert response.status_code == 200
        # searches that 'fetching snp report failed' not in log file
        # can search that 'SNPReportBytes:' in log file instead
        assert response.content.decode("utf-8").strip("\n") == "Did not find text in file"

    def test_key_acquired(self):
        response = request(f"http://{self.container_ip}:8000/key")
        assert response.status_code == 200
        # searches that 'releasing the key {KEY_NAME} failed.' not in log file
        # can search that 'Key Type: oct-HSM Key' in log file instead
        assert response.content.decode("utf-8").strip("\n") == "Did not find text in file"


if __name__ == "__main__":
    unittest.main()
