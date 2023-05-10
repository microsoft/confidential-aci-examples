from http.server import BaseHTTPRequestHandler, HTTPServer

import requests


class MyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/check_connection":
            request_to_sidecar = requests.get("http://localhost:8001/connect")
            connection_successful = (
                request_to_sidecar.status_code == 200
                and request_to_sidecar.content == b"Connection successful\n"
            )
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(str(connection_successful).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


def run():
    httpd = HTTPServer(("", 8000), MyRequestHandler)
    print("Server started...")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
