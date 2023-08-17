from http.server import SimpleHTTPRequestHandler, HTTPServer
from http.client import HTTPConnection

import requests


class MyRequestHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)

        conn = HTTPConnection("localhost", 8080)
        conn.request("POST", self.path, body=post_data, headers=self.headers)
        response = conn.getresponse()

        self.send_response(response.status)
        for key, value in response.getheaders():
            if key != "Transfer-Encoding":
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(response.read())

        conn.close()

    def do_GET(self):
        conn = HTTPConnection("localhost", 8080)
        conn.request("GET", self.path, headers=self.headers)
        response = conn.getresponse()

        self.send_response(response.status)
        for key, value in response.getheaders():
            self.send_header(key, value)
        self.end_headers()

        conn.close()


def run():
    httpd = HTTPServer(("", 8000), MyRequestHandler)
    print("Server started...")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
