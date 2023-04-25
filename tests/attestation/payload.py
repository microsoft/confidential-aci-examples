import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from get_attestation import get_attestation_report


class MyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/get_attestation"):
            query = urlparse(self.path).query
            query_dict = parse_qs(query)
            if "report_data" not in query_dict:
                self.send_response(400)
                self.end_headers()
                return
            report_data = query_dict["report_data"][0]

            self.send_response(200)
            self.send_header("Content-type", "application/octet-stream")
            self.end_headers()

            self.wfile.write(get_attestation_report(report_data.encode("utf-8")))
        else:
            self.send_response(404)
            self.end_headers()


def run():
    httpd = HTTPServer(("", 8000), MyRequestHandler)
    print("Server started...")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
