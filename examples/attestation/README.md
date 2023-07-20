# Attestation Example

This example demonstrates how to fetch and validate attestations from a confidential container instance. 

The [manfiest](manifest.json) file describes two containers which are deployed when the example runs. The first container runs an HTTP server which the client side can make requests to. The second is the sidecar container from the [confidential-sidecar-containers](https://github.com/microsoft/confidential-sidecar-containers) repository.

The HTTP server has three endpoints that are called by the client side:

- `/get_attestation`

    This endpoint uses the code in [get_attestation.py](get_attestation.py) to get the SNP report and return it. It takes the parameter `report_data` which is then included in the report which is used to validate that the report is one the caller requested.

- `/get_certificate_chain`

    This endpoint fetches a chain of certificates populated in a file locally available to the container. It starts from an AMD provided root of trust and ends with a certificate which signed the attestation report. This can be used to validate the report is a genuine SNP report.
    
- `/get_attestation_from_sidecar`

    This endpoint is the same as `/get_attestation` except the logic used to fetch the attestation report lives in a sidecar container.
    
    The main container talks to the sidecar over gRPC using protobuf, the [definition](protobuf/attestation_sidecar.proto) of the interface and the python code generated from that is in the [protobuf](protobuf/) directory.
    
- `/get_maa_token_from_sidecar`

    This endpoint is the same as `/get_attestation` except the logic used to fetch the attestation report lives in a sidecar container.

### Validating the Report

The code for validating an SNP report is in [validate_report.py](validate_report.py). It validates two aspects of the report:

- The report contains the provided report data to validate it's the report that was requested.
- The report is signed by the certificate which is part of a chain up to the AMD root of trust.

