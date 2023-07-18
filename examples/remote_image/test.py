import unittest
import os


from infra.test_case import TestCase


class RemoteImageTest(TestCase):
    def test_deployment_succeeded(self):
        assert self.container_ip is not None


if __name__ == "__main__":
    unittest.main()
