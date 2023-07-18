import argparse
from functools import partial
import http.server
import os
from http.server import HTTPServer
import re
from typing import Set


from infra.vm.operations import run_on_vm


class PassthroughHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.vm_name = kwargs.pop("vm_name")
        self.ip_address = kwargs.pop("ip_address")
        super().__init__(*args, **kwargs)

    def do_GET(self):
        url = f"http://{self.ip_address}:8000/{self.path}"
        response = run_on_vm(
            vm_name=self.vm_name,
            command=f"Invoke-WebRequest -UseBasicParsing -Uri {url}",
        )
        fields = [re.sub(" +", " ", line).split(":") for line in response.splitlines()]
        response_dict = dict()
        for key_value in fields:
            if len(key_value) == 2:
                response_dict[key_value[0].strip()] = key_value[1].strip()
        self.send_response(int(response_dict["StatusCode"]))
        self.send_header("Content-type", response_dict["Content-Type"])
        self.end_headers()
        self.wfile.write(response_dict["Content"].encode("utf-8"))


def run_passthrough_server(vm_name: str, ports: Set[int], ip_address: str):
    for port in ports:
        handler = partial(PassthroughHandler, vm_name=vm_name, ip_address=ip_address)
        with http.server.HTTPServer(("", port), handler) as httpd:
            print(f"Listening on port {port}")
            httpd.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a passthrough server")
    parser.add_argument(
        "--ip-address",
        required=True,
        help="The IP address of the target server",
    )
    parser.add_argument(
        "--ports",
        nargs="+",
        type=int,
        required=True,
        help="The ports to listen on",
    )
    args = parser.parse_args()

    run_passthrough_server(ports=set(args.ports), ip_address=args.ip_address)
