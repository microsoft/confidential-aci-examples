# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse
import unittest
import os
import uuid
import requests

from c_aci_testing.args.parameters.location import parse_location
from c_aci_testing.args.parameters.managed_identity import \
    parse_managed_identity
from c_aci_testing.args.parameters.registry import parse_registry
from c_aci_testing.args.parameters.repository import parse_repository
from c_aci_testing.args.parameters.resource_group import parse_resource_group
from c_aci_testing.args.parameters.subscription import parse_subscription
from c_aci_testing.tools.target_run import target_run_ctx
from c_aci_testing.tools.aci_get_ips import aci_get_ips

class PythonServerTest(unittest.TestCase):
    def test_python_server(self):

        parser = argparse.ArgumentParser()
        parse_subscription(parser)
        parse_resource_group(parser)
        parse_registry(parser)
        parse_repository(parser)
        parse_location(parser)
        parse_managed_identity(parser)
        args, _ = parser.parse_known_args()

        id = str(uuid.uuid4())

        with target_run_ctx(
            target_path=os.path.realpath(os.path.dirname(__file__)),
            deployment_name=f"python-server-{str(uuid.uuid4())}",
            tag=id,
            **vars(args),
        ) as deployment_ids:
            ip_address = aci_get_ips(ids=deployment_ids[0])
            response = requests.get(f"http://{ip_address}:8000/hello")
            assert response.status_code == 200
            assert response.content.decode("utf-8") == "Hello, World!"

        # Cleanup happens after block has finished


if __name__ == "__main__":
    unittest.main()