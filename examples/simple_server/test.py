# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest
import os
import uuid
import requests

from c_aci_testing.target_run import target_run
from c_aci_testing.aci_get_ips import aci_get_ips

class SimpleServerTest(unittest.TestCase):
    def test_simple_server(self):

        target_dir = os.path.realpath(os.path.dirname(__file__))
        run_id = str(uuid.uuid4())

        with target_run(
            target=target_dir,
            name=f"simple_server-{run_id}",
            tag=run_id,
            follow=False, # Don't follow because server runs indefinitely
        ) as deployment_id:
            response = requests.get(f"http://{aci_get_ips(ids=deployment_id)}:80")
            self.assertEqual(response.status_code, 200)
            print(f"Request successful: {response.text}")

        # Cleanup happens after block has finished


if __name__ == "__main__":
    unittest.main()