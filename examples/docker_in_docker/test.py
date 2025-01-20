# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse
from contextlib import contextmanager
import io
import sys
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
from c_aci_testing.tools.aci_monitor import aci_monitor

@contextmanager
def capture_stdout():
    old_stdout = sys.stdout
    buffer = io.StringIO()
    try:
        sys.stdout = buffer
        yield buffer
    finally:
        sys.stdout = old_stdout

class DockerInDockerTest(unittest.TestCase):
    def test_docker_in_docker(self):

        parser = argparse.ArgumentParser()
        parse_subscription(parser)
        parse_resource_group(parser)
        parse_registry(parser)
        parse_repository(parser)
        parse_location(parser)
        parse_managed_identity(parser)
        args, _ = parser.parse_known_args()

        id = str(uuid.uuid4())
        deployment_name = f"docker-in-docker-{id}"

        with target_run_ctx(
            target_path=os.path.realpath(os.path.dirname(__file__)),
            deployment_name=deployment_name,
            tag=id,
            **vars(args),
        ) as deployment_ids:
            with capture_stdout() as buffer:
                aci_monitor(deployment_name=deployment_name, **vars(args))
            container_logs = buffer.getvalue()
            print(container_logs)
            assert "Hello from Docker!" in container_logs

        # Cleanup happens after block has finished


if __name__ == "__main__":
    unittest.main()