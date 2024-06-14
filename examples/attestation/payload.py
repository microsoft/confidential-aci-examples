import os
from flask import Flask, request, Response

from get_attestation import get_attestation_report

app = Flask(f"{__name__}")

@app.route('/get_attestation', methods=['GET'])
def get_attestation():

    report_data = request.args.get("report_data")
    if report_data is None:
        return {"error": "report_data is required"}, 400

    return Response(
        get_attestation_report(report_data.encode("utf-8")),
        status=200,
        mimetype="application/octet-stream"
    )

@app.route('/get_cert_chain', methods=['GET'])
def get_cert_chain():
    with open(
        f"/{os.environ['UVM_SECURITY_CONTEXT_DIR']}/host-amd-cert-base64", "rb"
    ) as f:
        return Response(
            f.read(),
            status=200,
            mimetype="application/octet-stream"
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)