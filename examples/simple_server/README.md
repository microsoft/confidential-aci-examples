# Simple Server

This example demonstrates how to run a simple HTTP server from a confidential container. It's main purpose is to be a 'Hello World' type example which makes the deployment steps as clear as possible.

The [manifest](manifest.json) describes the key information for the example.

### Image Building

This example builds a simple container which is described in a [Dockerfile](Dockerfile). It is based on the official [Python Image](https://hub.docker.com/_/python/), and simply copies and runs a single [payload](payload.py) script.

### Deployment

The manifest is used to generate an Azure Resource Management (ARM) template which fully describes the Azure deployment needed.

While the infrastructure also generates a security policy based on the images being deployed, this example also contains a hardcoded security policy, in this case an '[allow all](security_policies/allow_all.rego)' policy. When the example is run in Github Actions, both the generated policy as well as policies specified in the manifest are tested. To run with a hardcoded policy locally, set the `SECURITY_POLICY` environment variable to a path relative to the examples directory.

### Testing

To act as an entrypoint to running the example, as well as ensuring the example works, [test.py](test.py) defines a unittest TestCase. This deploys and cleans up the Azure resources during the setup and teardown phases. The test itself attempts to make a request to the server that should be running in the container and validates the request was successful and returns the expected content.
