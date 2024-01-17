# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.http_request import request
from infra.test_case import TestCase

class KeyReleaseGRPCTest(TestCase):
    def test_grpc_interface_ready(self):
        assert self.container_ip is not None

        response = request(f"http://{self.container_ip}:8000/grpc_ready")

        assert response.status_code == 200, response.content.decode("utf-8")
        assert (
            "Hello GRPC interface test" in response.content.decode("utf-8").strip("\n")
        )

    def test_grpc_snp_report(self):
        assert self.container_ip is not None

        response = request(f"http://{self.container_ip}:8000/grpc_snp_report")

        assert response.status_code == 200, response.content.decode("utf-8")
        assert (
            "\"reportHexString\": \"0" in response.content.decode("utf-8").strip("\n")
        )
    # To-Do: Configure pipeline to have a pre-image build script where we can
    # get the SKR executable, make wrapped data and copy it into the primary container image for testing
    # def test_grpc_key_release(self):
    #     assert self.container_ip is not None

    #     response = request(f"http://{self.container_ip}:8000/grpc_key_release")

    #     assert response.status_code == 200, response.content.decode("utf-8")
    #     print(response.content.decode("utf-8"))
    #     assert (
    #         "Oceans are full of waterHorses have 4 legs" 
    #         == response.content.decode("utf-8").strip("\n")
    #     )


if __name__ == "__main__":
    unittest.main()
