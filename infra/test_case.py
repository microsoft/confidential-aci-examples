import json
import os
import unittest
import uuid

from infra.container.test_case import setUpAci, tearDownAci
from infra.vm.test_case import setUpVm, tearDownVm


class TestCase(unittest.TestCase):
    def setUp(self):
        self.container_ip = None

        self.test_name = self.__class__.__module__.split(".")[0]
        self.image_tag = str(uuid.uuid4())
        self.name = str(uuid.uuid4())

        with open(f"examples/{self.test_name}/manifest.json", "r") as manifest_file:
            self.manifest = json.load(manifest_file)

        self.deployment_name = os.getenv("DEPLOYMENT_NAME", f"deployment-{self.name}")

        self.backend = os.getenv("BACKEND", "ACI")
        {
            "ACI": setUpAci,
            "VM": setUpVm,
        }[
            self.backend
        ](self)

    def tearDown(self):
        {
            "ACI": tearDownAci,
            "VM": tearDownVm,
        }[
            self.backend
        ](self)
