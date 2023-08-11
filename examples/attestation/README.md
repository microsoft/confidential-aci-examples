# Attestation

This example demonstrates how to fetch and validate attestations from a confidential container instance. Attestations are needed to provide verification that a container is running in a genuine SEV-SNP environment. In the case of container instances, this is the Utility VM (UVM) which runs the containers.

### Fetching Attestation Reports

Attestations from SEV-SNP guests are obtained by calling a specific IOCTL with a report request. Full details can be found in AMD's [SEV-SNP documentation](https://www.amd.com/en/support/tech-docs/sev-secure-nested-paging-firmware-abi-specification).

This example shows two different methods of fetching an attestation report. The first is to make the IOCTL call directly from the main container, and the second is to use a sidecar container from the [confidential-sidecar-containers](https://github.com/microsoft/confidential-sidecar-containers) repository.

The [manifest](manifest.json) file describes two containers which are deployed when the example runs. The primary container runs a HTTP server for communication with the client as well as being capable of fetching an attestation locally, the other container is the attestation sidecar.

The HTTP server has three endpoints that are called by the client side:

- `/get_attestation`

  This endpoint uses the code in [get_attestation.py](get_attestation.py) to get the SNP report and return it. It takes the parameter `report_data` which is then included in the report which is used to validate that the report is one the caller requested.

- `/get_certificate_chain`

  This endpoint fetches a chain of certificates populated in a file locally available to the container. It starts from an AMD provided root of trust and ends with a certificate which signed the attestation report. This can be used to validate the report is a genuine SNP report.

- `/get_attestation_from_sidecar`

  This endpoint is the same as `/get_attestation` except the logic used to fetch the attestation report lives in a sidecar container.

  The main container talks to the sidecar over gRPC using protobuf, the [definition](protobuf/attestation_sidecar.proto) of the interface and the python code generated from that is in the [protobuf](protobuf/) directory.

### Validating Attestation Reports

The code for validating an SNP report is in [validate_attestation.py](validate_attestation.py). It is important to validate that the report is both genuine and the one requested by the user. Supplimentary artifacts are used to validate the report, and these are found as base64 encoded files in the containers filesystem, the path to which is provided via the environment variable `UVM_SECURITY_CONTEXT_DIR`.

It is essential that a container must not be given access to sensitive data before it is established that it is genuine. The container itself cannot do that as an attacker in charge of the host can easily load a modified container. There is a need for another entity to check that the container is genuine and running in a secure environment that respects the correct rules.

There are three aspects of the attestation to be validated:

#### 1. Validate the report came from a genuine AMD processor

Under `$UVM_SECURITY_CONTEXT_DIR/host-amd-cert-base64`, there is a base64 encoded file which decodes to json containing the following fields:

- `vcekCert`: The PEM certificate which signed the report.
- `tcbm`: The numeric version of the UVM, should match the CURRENT_TCB value found in the attestation report.
- `certificateChain`: A chain of 3 PEM certificates which sign each one before it:
  - `VCEK`: Versioned Chip Endorsement Key
  - `ASK`: AMD SEV Signing Key
  - `ARK`: AMD Root Key

If each stage of the chain from ARK -> ASK -> VCEK -> Report signs the next stage, that confirms that the report came from a genuine AMD processor as long as the root key is trusted.

#### 2. Validate that the Utility VM has been endorsed by Microsoft. (Not yet in example code)

Under `$UVM_SECURITY_CONTEXT_DIR/reference-info-base64`, there is a base64 encoded file which decodes to a COSE_Sign1 document.

COSE_Sign1 envelopes are signed wrappers for arbitary data. See https://datatracker.ietf.org/doc/html/rfc8152. There is a header which contains the iss (issuer) and feed fields that must match Confidential ACI's signing identity and the certificate chain used to sign the whole bundle.

The payload of the COSE_Sign1 envelope is json containing the following fields:

- `x-ms-sevsnpvm-guestsvn`: Version of the UVM
- `x-ms-sevsnpvm-launchmeasurement`: The measurement of the UVM at launch time, this should match the `MEASUREMENT` field of the attestation report.

To validate the UVM, unpack the COSE_Sign1 envelope and check that the issuer matches the Confidential ACI signing identity which is the [DID:x509](https://github.com/microsoft/did-x509/blob/main/specification.md) string:

```
did:x509%253A0%253Asha256%253AI__iuL25oXEVFdTP_aBLx_eT1RPHbCQ_ECBQfYZpt9s%253A%253Aeku%253A1.3.6.1.4.1.311.76.59.1.2
```

#### 3. Validate the expected Security Policy is used

Under `$UVM_SECURITY_CONTEXT_DIR/security-policy-base64`, there is a base64 encoded file which decodes to a security policy written in [Rego](https://www.openpolicyagent.org/docs/latest/policy-language). The SHA256 hash of this Rego file should match the `HOST_DATA` field of the attestation report.

### Using Microsoft Azure Attestation for Validation

You can also use the [Microsoft Azure Attestation](https://learn.microsoft.com/en-us/azure/attestation/overview) service to validate attestations, but this isn't demonstrated in this example.
