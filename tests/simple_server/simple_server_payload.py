"""Simple Python HTTP server for testing purposes."""

import os
from http.server import BaseHTTPRequestHandler, HTTPServer

ENDPOINTS = {
    "/hello": {
        "method": "GET",
        "response": {
            "status": 200,
            "content_type": "text/plain",
            "body": f"Hello world!{os.linesep}",
        },
    }
}


class MyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ENDPOINTS and ENDPOINTS[self.path]["method"] == "GET":
            self.send_response(200)
            response = ENDPOINTS[self.path]["response"]
            self.send_header("Content-type", response["content_type"])
            self.end_headers()
            self.wfile.write(response["body"].encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


def run():
    httpd = HTTPServer(("", 8000), MyRequestHandler)
    print("Server started...")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
