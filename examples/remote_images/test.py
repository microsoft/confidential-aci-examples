# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest
import os
import uuid

from c_aci_testing.target_run import target_run_ctx

class RemoteImagesTest(unittest.TestCase):
    def test_remote_images(self):

        target_dir = os.path.realpath(os.path.dirname(__file__))
        id = str(uuid.uuid4())

        with target_run_ctx(
            target=target_dir,
            name=f"remote_images-{id}",
            tag=id,
            follow=True,
            prefer_pull=True,
        ) as deployment_ids:
            ...

        # Cleanup happens after block has finished


if __name__ == "__main__":
    unittest.main()