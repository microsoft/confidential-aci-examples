# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse
import unittest
import os
import uuid

from c_aci_testing.args.parameters.location import parse_location
from c_aci_testing.args.parameters.managed_identity import \
    parse_managed_identity
from c_aci_testing.args.parameters.registry import parse_registry
from c_aci_testing.args.parameters.repository import parse_repository
from c_aci_testing.args.parameters.resource_group import parse_resource_group
from c_aci_testing.args.parameters.subscription import parse_subscription
from c_aci_testing.tools.target_run import target_run_ctx

class RemoteImagesTest(unittest.TestCase):
    def test_remote_images(self):

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
            deployment_name=f"remote_images-{id}",
            tag=id,
            follow=True,
            prefer_pull=True,
            **vars(args),
        ) as deployment_ids:
            ...

        # Cleanup happens after block has finished


if __name__ == "__main__":
    unittest.main()