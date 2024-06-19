# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Simple Python HTTP server for testing purposes."""

from flask import Flask

app = Flask(f"attestation_{__name__}")

@app.route('/hello', methods=['GET'])
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)