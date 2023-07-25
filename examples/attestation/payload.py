import os
import sys
import grpc
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from get_attestation import get_attestation_report

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), "protobuf"))
import protobuf.attestation_sidecar_pb2 as attestation_sidecar
import protobuf.attestation_sidecar_pb2_grpc as attestation_sidecar_grpc


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

            if self.path.startswith("/get_attestation_from_sidecar"):
                request = attestation_sidecar.FetchAttestationRequest()
                request.report_data = report_data.encode("utf-8")
                with grpc.insecure_channel("unix:/mnt/uds/sock") as channel:
                    stub = attestation_sidecar_grpc.AttestationContainerStub(channel)
                    response = stub.FetchAttestation(request)
                    attestation = response.attestation

            else:  # /get_attestation
                attestation = get_attestation_report(report_data.encode("utf-8"))

            self.send_response(200)
            self.send_header("Content-type", "application/octet-stream")
            self.end_headers()
            self.wfile.write(attestation)

        elif self.path.startswith("/get_certificate_chain"):
            self.send_response(200)
            self.send_header("Content-type", "application/octet-stream")
            self.end_headers()

            with open(
                f"/{os.environ['UVM_SECURITY_CONTEXT_DIR']}/host-amd-cert-base64", "rb"
            ) as f:
                self.wfile.write(f.read())

        else:
            self.send_response(404)
            self.end_headers()


def run():
    httpd = HTTPServer(("", 8000), MyRequestHandler)
    print("Server started...")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
