import os
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer

MOUNT_DIR = "/mnt/remote"


def read_file(path: str) -> str:
    # path should be in mount directory if mount succeeded
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read()
    else:
        return "File in Mount Path does not exist"


def write_file(path: str, content: str) -> str:
    # mount directory should exist if mount succeeded
    if os.path.exists(Path(path).absolute()):
        # make file in mount directory
        with open(path, "w") as f:
            f.write(content)
        return read_file(path)
    else:
        return "Mount Path does not exist"


ENDPOINTS = {
    "/read1": lambda: read_file(os.path.join(MOUNT_DIR, "share1", "file.txt")),
    "/write1": lambda: write_file(
        os.path.join(MOUNT_DIR, "share1", "new_file.txt"),
        "This is a new file in the encrypted filesystem!",
    ),
    "/read2": lambda: read_file(os.path.join(MOUNT_DIR, "share2", "file.txt")),
    "/write2": lambda: write_file(
        os.path.join(MOUNT_DIR, "share2" ,"new_file.txt"),
        "This is a new file in the encrypted filesystem!",
    ),
}


class MyRequestHandler(BaseHTTPRequestHandler):
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
            self.send_response(404)
            self.end_headers()


def run():
    httpd = HTTPServer(("", 8000), MyRequestHandler)
    print("Server started...")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
