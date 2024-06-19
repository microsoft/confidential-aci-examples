# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest
import os
import uuid
import requests

from c_aci_testing.target_run import target_run_ctx
from c_aci_testing.aci_get_ips import aci_get_ips

try:
    from validate_attestation import validate_attestation
except ImportError:
    from .validate_attestation import validate_attestation

class AttestationTest(unittest.TestCase):
    def test_attestation(self):

        target_dir = os.path.realpath(os.path.dirname(__file__))
        id = str(uuid.uuid4())

        with target_run_ctx(
            target=target_dir,
            name=f"attestation-{id}",
            tag=id,
            follow=False,
        ) as deployment_ids:
            ip_address = aci_get_ips(ids=deployment_ids[0])

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