import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.test_case import TestCase


class EncryptedFilesystemTest(TestCase):
    def test_encfs_deployment_succeeded(self):
        assert self.container_ip is not None

    # To-Do: Add more/better tests here


if __name__ == "__main__":
    unittest.main()
