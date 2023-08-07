import os
from http.server import BaseHTTPRequestHandler, HTTPServer

MOUNT_DIR = "/mnt/remote/share"
LOG_FILE = MOUNT_DIR + "/log.txt"
KEY_NAME = os.environ["KID"]


def read_file(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def write_file(path: str, content: str) -> str:
    try:
        # make directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # make file if it doesn't exist
        with open(path, "w") as f:
            f.write(content)
        return read_file(path)
    except Exception as e:
        return "Failed to write file"


def scan_file(path: str, text: str) -> str:
    try:
        with open(path, "r") as f:
            if text in f.read():
                return "Found text in file"
            else:
                return "Did not find text in file"
    except Exception as e:
        return "Failed to scan file"


ENDPOINTS = {
    "/read": lambda: read_file(os.path.join(MOUNT_DIR, "file.txt")),
    "/write": lambda: write_file(
        os.path.join(MOUNT_DIR, "new_file.txt"),
        "This is a new file in the encrypted filesystem!",
    ),
}


class MyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ENDPOINTS and ENDPOINTS[self.path]["method"] == "GET":
            try:
                result = ENDPOINTS[self.path]()
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(result.encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


def run():
    httpd = HTTPServer(("", 8000), MyRequestHandler)
    print("Server started...")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
