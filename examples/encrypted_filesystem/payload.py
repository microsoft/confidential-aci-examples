import os
from http.server import BaseHTTPRequestHandler, HTTPServer

MOUNT_DIR = "/mnt/remote/share"


def read_file(path: str) -> str:
    # path should be in mount directory if mount succeeded
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read()
    else:
        dirs_str = "\n".join([os.getcwd()] + os.listdir(os.getcwd) + os.listdir("/mnt/remote"))
        return dirs_str


def write_file(path: str, content: str) -> str:
    # mount directory should exist if mount succeeded
    if os.path.exists(MOUNT_DIR):
        try:
            # make file in mount directory
            with open(path, "w") as f:
                f.write(content)
            return read_file(path)
        except Exception as e:
            return "Failed to write file"
    else:
        return "Mount Path does not exist"


ENDPOINTS = {
    "/read": lambda: read_file(os.path.join(MOUNT_DIR, "file.txt")),
    "/write": lambda: write_file(
        os.path.join(MOUNT_DIR, "new_file.txt"),
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
