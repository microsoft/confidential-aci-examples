# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.http_request import request
from infra.test_case import TestCase


class SimpleSidecarTest(TestCase):
    def test_sidecar_connection(self):
        assert self.container_ip is not None
        response = request(f"http://{self.container_ip}:8000/check_connection")
        assert response.status_code == 200
        assert response.content.decode("utf-8") == "True"


if __name__ == "__main__":
    unittest.main()
