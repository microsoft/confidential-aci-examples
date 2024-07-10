# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest
import os
import uuid
import requests

from c_aci_testing.tools.target_run import target_run_ctx
from c_aci_testing.tools.aci_get_ips import aci_get_ips

class PythonServerTest(unittest.TestCase):
    def test_python_server(self):

        target_dir = os.path.realpath(os.path.dirname(__file__))
        id = str(uuid.uuid4())

        with target_run_ctx(
            target=target_dir,
            name=f"python-server-{id}",
            tag=id,
            follow=False
        ) as deployment_ids:
            ip_address = aci_get_ips(ids=deployment_ids[0])
            response = requests.get(f"http://{ip_address}:8000/hello")
            assert response.status_code == 200
            assert response.content.decode("utf-8") == "Hello, World!"

        # Cleanup happens after block has finished


if __name__ == "__main__":
    unittest.main()