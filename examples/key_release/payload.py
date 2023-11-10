# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import subprocess

import requests

def create_grpc_test_files():
    if not os.path.isfile("wrapped"):
        with open("wrapped", "w") as f:
            f.write("eyJraWQiOiJ0ZXN0a2V5MDAwIiwid3JhcHBlZF9kYXRhIjoiVm1TRlhFc0tRWXMzWERyZU5nWmZ3UXBvNGtGWGo5U1ROYWZ0dzVoUks1cExxOEJMWUVSQkVJNzl0RTBCMkh1SURDR2w4TTRMWSt1a3Q0YjdNeUw4V01DdWZZcWtOTEM3RUZiOE40TWwzVW5lL2ZvdDBBQk9tKzhad2I4clFCanlvdzJhY2FVcUxiNVNRUnpCekpaL1hCS0MyYjZlUDhxWksyOFF3Q09vOEVaemp0N0wrWDBjc0FkODlHWWRER1pZRWNSaVp3VE9NVER3Zzc4c042S3BBeE9ndm1qcitvY0dCeVoxS2FBek5pZjhQaE5HWjdqYVduaVhOZFZoSlFaVVI1NmEvMVBIVHpjQ3QwdUhmejRWdENzS1lMa3BCOGlSYjB5SmdRNVhTUkpNaEJidkZNV0ZxTXdPQ1puSFhKZFFUOENNQWtCb1E0akU0TFNUeDdCUGl3SmpPQjFreFZVcXZsZFhGRmRsRHcwZWNYaTNDaVpUdkFWdGYxV1dyVXVJc3lXRm5rWlMrV0lLNldTSGJjTEFzcldIQ3RGbkFiL20wTGdVcVF0b01SaFVRUVh1Z0pRUkVmVUlScjhiUXNqK3g5VzlDU0JaQ2VtemJIK3FCSk04ZHhPSWgySDZqeHg2QUxVQ3ovODV5ZVk0SlRsR3pieG5UQXpnZElkQ1dwOXciLCJ3cmFwX3R5cGUiOiJyc2FfMzA3MiIsImttc19lbmRwb2ludCI6ImFjY21oc20ubWFuYWdlZGhzbS5henVyZS5uZXQiLCJhdHRlc3Rlcl9lbmRwb2ludCI6InNoYXJlZGV1czIuZXVzMi5hdHRlc3QuYXp1cmUubmV0In0=")

    output = subprocess.run("./unwrap.sh wrapped plaintext && cat plaintext", stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, input="", shell=True)
    return output

def grpc_ready_test():
    output = subprocess.run("grpcurl -v -plaintext -d '{\"name\":\"GRPC interface test!\"}' 127.0.0.1:50000  keyprovider.KeyProviderService.SayHello", stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, input="", shell=True)
    return output.stdout if output.returncode == 0 else output.stderr

def grpc_snp_report():
    output = create_grpc_test_files()
    if output.returncode == 0:
        output = subprocess.run("grpcurl -v -plaintext -d '{\"reportDataHexString\":\"\"}' 127.0.0.1:50000  keyprovider.KeyProviderService.GetReport", stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, input="", shell=True)
    return output.stdout if output.returncode == 0 else output.stderr

def grpc_key_release():
    output = create_grpc_test_files()
    #if output.returncode == 0:
        #output = subprocess.run("cat plaintext", stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, input="", shell=True)
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
