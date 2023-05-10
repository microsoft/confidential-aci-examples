import os
import unittest

from infra.aci_test_case import setUpAci, tearDownAci


class TestCase(unittest.TestCase):
    def setUp(self):
        self.container_ip = None
        self.backend = os.getenv("BACKEND", "ACI")
        if self.backend == "ACI":
            setUpAci(self)

    def tearDown(self):
        if self.backend == "ACI":
            tearDownAci(self)
