import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.aci_test_case import AciTestCase


class RemoteImageTest(AciTestCase):
    def test_deployment_succeeded(self):
        assert self.container_ip is not None


if __name__ == "__main__":
    unittest.main()
