# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import subprocess

import requests

def create_grpc_test_files():
    if not os.path.isfile("wrapped"):
        with open("wrapped", "w") as f:
            f.write("eyJraWQiOiJ0ZXN0a2V5MDAwIiwid3JhcHBlZF9kYXRhIjoiUEplWGhUMVhEQ0FnYUJBUkdGSTF6SXpveG9KMTVxUHhGcDNRaTU0QWl4Wmw1cWN1V1VCZWFRVGxqVm1DdkZJNEh4OUR3TW1QQlJvbjFIUlo3MTl0d3Z6M0NaYThCdHFMdkY3NVB2VFZZWTgyTjNCN25HYndxTkNXUWM3bkc5MXM0RHNOZkU5c2pZbThSbUhNUVJJeGFlTHVJUUNiOEV3MmNJTTBaK3dBZFJxQlhtOHJCcFd3ci8rSzMrNk51ZW9qZCtqR0FudEhuRnBuRmF1WGZpTXA2RkQyVnN6MEMxQ0VpbWtZalRqTjFCbmkvQVViYUgrS2kxR3VoQzRwaE92cUpTMG9RamplMWFHWUFTRHROZU9oeGw5L0ZCSENPQXV6Yk4xeFpQbUowMTdTTnp2b0taVlBPTGloVWxNcWhQU3I3OW5CV25yM0FRU2NmaXN0R3BUVzFaMGVhTDBBcWhtSC9mb1BWYkI3aFhqMHZrOVY3eVl0dTlJQWhWVVhVMU8rMjdQQUdVcllSa1pSRmtmQzdRcTJLVkQza1d3aXhRL1M5c2RnZ1NUTTlFYU41SEtmdGlpQWs4aDVYTC9jTUs0NU5QU255TFRYZTRmWVMvT0lWdlRpcFBXU2luQkRDc2hISDRxaGNyUFJPTW03Tlp6S0JzdkNMVHVvL0lBQWlWS2giLCJ3cmFwX3R5cGUiOiJyc2FfMzA3MiIsImttc19lbmRwb2ludCI6ImFjY21oc20ubWFuYWdlZGhzbS5henVyZS5uZXQiLCJhdHRlc3Rlcl9lbmRwb2ludCI6InNoYXJlZGV1czIuZXVzMi5hdHRlc3QuYXp1cmUubmV0In0=")

    output = subprocess.run("./unwrap.sh wrapped plaintext", stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, input="", shell=True)
    return output

def grpc_ready_test():
    output = subprocess.run("grpcurl -v -plaintext -d '{\"name\":\"GRPC interface test!\"}' 127.0.0.1:50000  keyprovider.KeyProviderService.SayHello", stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, input="", shell=True)
    return output.stdout if output.returncode == 0 else output.stderr

def grpc_snp_report():
    output = create_grpc_test_files()
    if output.returncode == 0:
        output = subprocess.run("grpcurl -v -plaintext -d '{\"reportDataHexString\":\"\"}' 127.0.0.1:50000  keyprovider.KeyProviderService.GetReport", stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, input="", shell=True)
    return output

def grpc_key_release():
    output = create_grpc_test_files()
    #if output.returncode == 0:
        #output = subprocess.run("cat plaintext", stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, input="", shell=True)
    return output

ENDPOINTS = {
    "/grpc_ready": lambda: grpc_ready_test(),
    "/grpc_snp_report": lambda: grpc_snp_report(),
    "/grpc_key_release": lambda: grpc_key_release(),
}


class MyRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        response = requests.post(
            url=f"http://localhost:8080{self.path}",
            headers=dict(self.headers),
            data=self.rfile.read(int(self.headers.get("Content-Length", 0))),
        )
        self.send_response(response.status_code)
        for header, value in response.headers.items():
            if header != "Transfer-Encoding":
                self.send_header(header, value)
        self.end_headers()

        self.wfile.write(response.content)

    def do_GET(self):
        if self.path in ENDPOINTS:
            try:
                result = ENDPOINTS[self.path]()
                self.send_response(200)
            except Exception as e:
                result = str(e)
                self.send_response(400)

            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(result.encode("utf-8"))
        else:
            response = requests.get(
                url=f"http://localhost:8080{self.path}",
                headers=dict(self.headers),
                data=self.rfile.read(int(self.headers.get("Content-Length", 0))),
            )
            self.send_response(response.status_code)
            for header, value in response.headers.items():
                if header != "Transfer-Encoding":
                    self.send_header(header, value)
            self.end_headers()

            self.wfile.write(response.content)


def run():
    httpd = HTTPServer(("", 8000), MyRequestHandler)
    print("Server started...")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
