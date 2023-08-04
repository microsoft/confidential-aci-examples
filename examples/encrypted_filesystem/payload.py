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
    "/read": {
        "method": "GET",
        "response": {
            "content_type": "text/plain",
            "body": read_file(os.path.join(MOUNT_DIR, "file.txt")),
        },
    },
    "/write": {
        "method": "GET",
        "response": {
            "content_type": "text/plain",
            "body": write_file(os.path.join(MOUNT_DIR, "new_file.txt"), "This is a new file in the encrypted filesystem!")
        },
    },
    "/maa_token": {
        "method": "GET",
        "response": {
            "content_type": "text/plain",
            "body": scan_file(LOG_FILE, "retrieving MAA token from MAA endpoint failed")
        },
    },
    "/snp_report": {
        "method": "GET",
        "response": {
            "content_type": "text/plain",
            "body": scan_file(LOG_FILE, "fetching snp report failed")
        },
    },
    "/key": {
        "method": "GET",
        "response": {
            "content_type": "text/plain",
            "body": scan_file(LOG_FILE, f"releasing the key {KEY_NAME} failed.")
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