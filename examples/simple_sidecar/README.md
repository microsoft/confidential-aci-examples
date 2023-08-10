# Simple Sidecar

This example demonstrates how to run multiple containers in the same container group. These containers run on the same Utility Virtual Machine (UVM) and therefore share a kernel. Confidential ACI maintains [several container images](https://github.com/microsoft/confidential-sidecar-containers) which are intended to be deployed alongside a primary container in this way, they can perform specialised tasks such as attestation which means that code doesn't have to live in the primary container.

This example is simpler than those sidecars however, there are two containers:

- Primary: Provides an HTTP server for the client test to connect to, and attempts to communicate with the sidecar secondary container.

- Secondary: Provides an HTTP server for the primary container to connect to, it uses a port which is not exposed by the container group so is only accessible to the primary container.
