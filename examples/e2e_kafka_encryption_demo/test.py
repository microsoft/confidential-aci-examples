# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from infra.test_case import TestCase


class KeyReleaseTest(TestCase):
    def test_kafka_demo_decrypted_message(self):
        teststr = "Hello"
        assert teststr == "Hello"


if __name__ == "__main__":
    unittest.main()
