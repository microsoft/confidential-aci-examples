# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from http.server import BaseHTTPRequestHandler, HTTPServer

import requests
import subprocess

def grpc_ready_test():
    output = subprocess.run("grpcurl -v -plaintext -d '{\"name\":\"GRPC interface test!\"}' 127.0.0.1:50000  keyprovider.KeyProviderService.SayHello", stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, input="", shell=True)
    return output.stdout if output.returncode == 0 else output.stderr

def grpc_snp_report():
    output = subprocess.run("grpcurl -v -plaintext -d '{\"reportDataHexString\":\"\"}' 127.0.0.1:50000  keyprovider.KeyProviderService.GetReport", stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, input="", shell=True)
    return output.stdout if output.returncode == 0 else output.stderr

def grpc_key_release():
    output = subprocess.run("./unwrap.sh wrapped plaintext && cat plaintext", stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, input="", shell=True)
    return output.stdout if output.returncode == 0 else output.stderr

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
