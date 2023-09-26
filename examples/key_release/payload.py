# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from http.server import BaseHTTPRequestHandler, HTTPServer

import requests


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
