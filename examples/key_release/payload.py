# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess

import requests

def create_grpc_test_files():
    with open("plaintext", "w") as f:
        f.write("Oceans are full of water\nHorses have 4 legs")

    with open("wrapped", "w") as f:
        f.write("eyJraWQiOiJ0ZXN0a2V5MDAwIiwid3JhcHBlZF9kYXRhIjoiSVZuYzM2Smg3SXJUMkpzSkszaG0vNFdHcVdDblJtL0RteHNiWDZoTXJNc0RCbm5SWGhEbFAySElZMEpxejFxMUhMdjFFUHQ3cUg0Z0ZKN3VhOTdhZERjZnRrdDJJNlUrbnVIeGtWZnJLV1IxcnVBTUhzVTBJYVFsM1hUb1JUTzlEYzAvRHdXdVRZWUJCcUY5UDBlcXI0bVk0b0MrTzhXVWlrWjVBd01pcE5BMWFCWGZTNFc1dEtwS0YxVEhzcHpWNkNsamhic2NqaWN2UUxPT3FBdHNJUkpHZTJCN0hwTzBrdEtVRUxVZXBZcHNtR0NPRUZxQnBENkRsd2xqZXB0RW5GaXlvcmNqKzJDODVFMFQzcDNFRllEUktsMTNxWFVHaWRnL1k5bnNZdlJhSXdWWlQ3WTN2dEdVZy9jT0RzSFovS0Q5aXFxalJWVitiOWpTVEZMRmFyY0UybXpwTlFBT2lXL3FBSnB3TFlObmpFSzNkQzI2bEN5a1h1bkZvbjlGWVVHZi9rMEZUb0hGT0Qyd05XcWNSS0hLYXBvc1gycHd1SDQ4b1I3cEUvWS8rSDh4RGVqZ1VOTm14MjFWeXNjODVWR1M5M01ZNlozNm42VzlCenk5UktmbFJaQXpLRkZTYlYyYnhrRkhadURteUkyUDhtWnkzTWxqczFESnZjWWYiLCJ3cmFwX3R5cGUiOiJyc2FfMzA3MiIsImttc19lbmRwb2ludCI6ImFjY21oc20ubWFuYWdlZGhzbS5henVyZS5uZXQiLCJhdHRlc3Rlcl9lbmRwb2ludCI6InNoYXJlZGV1czIuZXVzMi5hdHRlc3QuYXp1cmUubmV0In0=")

def grpc_ready_test():
    return subprocess.run("grpcurl -v -plaintext -d '{\"name\":\"GRPC interface test!\"}' 127.0.0.1:50000  keyprovider.KeyProviderService.SayHello", stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, input="", shell=True).stdout

def grpc_snp_report():
    create_grpc_test_files()
    output = subprocess.run("./unwrap.sh wrapped plaintext", stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, input="", shell=True)
    return subprocess.run("grpcurl -v -plaintext -d '{\"reportDataHexString\":\"\"}' 127.0.0.1:50000  keyprovider.KeyProviderService.GetReport", stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, input="", shell=True).stdout if output.returncode == 0 else output.stderr

def grpc_key_release():
    cmd = "AAA=`printf skr | base64 -w0`; ANNO=`cat wrapped`; REQ=`echo '{\"op\":\"keyunwrap\",\"keywrapparams\":{},\"keyunwrapparams\":{\"dc\":{\"Parameters\":{\"attestation-agent\":[\"${AAA}\"]}},\"annotation\":\"${ANNO}\"}}' | base64 -w0`; grpcurl -plaintext -d '{\"KeyProviderKeyWrapProtocolInput\":\"${REQ}\"}' 127.0.0.1:50000 keyprovider.KeyProviderService.UnWrapKey"
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, input="", shell=True).stdout

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
