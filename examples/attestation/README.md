# Attestation

This example demonstrates how to fetch and validate attestations from a confidential container instance. Attestations from SEV-SNP guests are obtained by calling a specific IOCTL with a report request. Full details can be found in AMD's [SEV-SNP documentation](https://www.amd.com/en/support/tech-docs/sev-secure-nested-paging-firmware-abi-specification). 

This example shows two different methods of fetching an attestation report. The first is to make the IOCTL call directly from the main container, and the second is to use an existing sidecar from the [confidential-sidecar-containers](https://github.com/microsoft/confidential-sidecar-containers) repository.

The [manfiest](manifest.json) file describes two containers which are deployed when the example runs. The primary container runs a HTTP server for communication with the client as well as being capable of fetching an attestation locally, the other container is the attestation sidecar.

The HTTP server has three endpoints that are called by the client side:

- `/get_attestation`

    This endpoint uses the code in [get_attestation.py](get_attestation.py) to get the SNP report and return it. It takes the parameter `report_data` which is then included in the report which is used to validate that the report is one the caller requested.

- `/get_certificate_chain`

    This endpoint fetches a chain of certificates populated in a file locally available to the container. It starts from an AMD provided root of trust and ends with a certificate which signed the attestation report. This can be used to validate the report is a genuine SNP report.
    
- `/get_attestation_from_sidecar`

    This endpoint is the same as `/get_attestation` except the logic used to fetch the attestation report lives in a sidecar container.
    
    The main container talks to the sidecar over gRPC using protobuf, the [definition](protobuf/attestation_sidecar.proto) of the interface and the python code generated from that is in the [protobuf](protobuf/) directory.

### Validating the Report

The code for validating an SNP report is in [validate_report.py](validate_report.py). It validates two aspects of the report:

- The report contains the provided report data to validate it's the report that was requested.
- The report is signed by the certificate which is part of a chain up to the AMD root of trust.

You can also use the [Microsoft Azure Attestation](https://learn.microsoft.com/en-us/azure/attestation/overview) service to validate attestations, but this isn't demonstrated in this example.