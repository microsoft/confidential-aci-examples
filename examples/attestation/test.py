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

try:
    from validate_attestation import validate_attestation
except ImportError:
    from .validate_attestation import validate_attestation

class AttestationTest(unittest.TestCase):
    def test_attestation(self):

        parser = argparse.ArgumentParser()
        parse_subscription(parser)
        parse_resource_group(parser)
        parse_registry(parser)
        parse_repository(parser)
        parse_location(parser)
        parse_managed_identity(parser)
        args, _ = parser.parse_known_args()

        id = str(uuid.uuid4())
        deployment_name = f"attestation-{id}"

        with target_run_ctx(
            target_path=os.path.realpath(os.path.dirname(__file__)),
            deployment_name=f"attestation-{id}",
            tag=id,
            policy_type="allow_all",
            **vars(args),
        ) as deployment_ids:
            ip_address = aci_get_ips(
                deployment_name=deployment_name,
                **vars(args),
            )[0]

            input_report_data = "Hello world!"

            attestation = requests.get(
                f"http://{ip_address}:8000/get_attestation?report_data={input_report_data}",
            )
            assert attestation.status_code == 200

            cert_chain = requests.get(
                f"http://{ip_address}:8000/get_cert_chain",
            )
            assert cert_chain.status_code == 200

            validate_attestation(
                attestation_bytes=attestation.content,
                certificate_chain=cert_chain.content,
                expected_report_data=input_report_data,
            )

        # Cleanup happens after block has finished


if __name__ == "__main__":
    unittest.main()
