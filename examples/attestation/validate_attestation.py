# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import base64
import json
import os
import re
import struct
import sys
from typing import Tuple
from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.hashes import SHA384
from cryptography.hazmat.primitives.asymmetric.ec import ECDSA
from cryptography.hazmat.primitives.asymmetric.padding import PSS, MGF1
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from get_attestation import SIGNATURE_STRUCTURE, SNP_REPORT_STRUCTURE

# Hardcode the AMD root of trust public key, so that locally obtained
# certificate chain used to sign the report can be traced to a known good value.
AMD_ROOT_PUBLIC_KEY = load_pem_public_key(
    """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA0Ld52RJOdeiJlqK2JdsV
mD7FktuotWwX1fNgW41XY9Xz1HEhSUmhLz9Cu9DHRlvgJSNxbeYYsnJfvyjx1MfU
0V5tkKiU1EesNFta1kTA0szNisdYc9isqk7mXT5+KfGRbfc4V/9zRIcE8jlHN61S
1ju8X93+6dxDUrG2SzxqJ4BhqyYmUDruPXJSX4vUc01P7j98MpqOS95rORdGHeI5
2Naz5m2B+O+vjsC060d37jY9LFeuOP4Meri8qgfi2S5kKqg/aF6aPtuAZQVR7u3K
FYXP59XmJgtcog05gmI0T/OitLhuzVvpZcLph0odh/1IPXqx3+MnjD97A7fXpqGd
/y8KxX7jksTEzAOgbKAeam3lm+3yKIcTYMlsRMXPcjNbIvmsBykD//xSniusuHBk
gnlENEWx1UcbQQrs+gVDkuVPhsnzIRNgYvM48Y+7LGiJYnrmE8xcrexekBxrva2V
9TJQqnN3Q53kt5viQi3+gCfmkwC0F0tirIZbLkXPrPwzZ0M9eNxhIySb2npJfgnq
z55I0u33wh4r0ZNQeTGfw03MBUtyuzGesGkcw+loqMaq1qR4tjGbPYxCvpCq7+Og
pCCoMNit2uLo9M18fHz10lOMT8nWAUvRZFzteXCm+7PHdYPlmQwUw3LvenJ/ILXo
QPHfbkH0CyPfhl1jWhJFZasCAwEAAQ==
-----END PUBLIC KEY-----
""".encode(),
)


def get_certificate_chain(certificate_chain: bytes) -> Tuple[x509.Certificate, ...]:
    certificate_chain_json = json.loads(base64.b64decode(certificate_chain).decode())
    return tuple(
        [
            x509.load_pem_x509_certificate(cert.encode())
            for cert in [
                certificate_chain_json["vcekCert"],
                *re.findall(
                    f"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----",
                    certificate_chain_json["certificateChain"],
                    flags=re.DOTALL,
                ),
            ]
        ]
    )


def cert_signed_other_cert(
    parent_cert: x509.Certificate,
    child_cert: x509.Certificate,
) -> bool:
    try:
        parent_cert.public_key().verify(  # type: ignore
            child_cert.signature,
            child_cert.tbs_certificate_bytes,
            PSS(
                mgf=MGF1(SHA384()),
                salt_length=SHA384.digest_size,  # type: ignore
            ),  # type: ignore
            SHA384(),  # type: ignore
        )
        return True

    except InvalidSignature:
        return False


def validate_attestation(
    attestation_bytes: bytes,
    certificate_chain: bytes,
    expected_report_data: str,
) -> bool:
    (
        version,
        guest_svn,
        policy,
        family_id,
        image_id,
        vmpl,
        signature_algorithm,
        current_tcb,
        platform_info,
        author_key,
        report_data,
        measurement,
        host_data,
        id_key_digest,
        author_key_digest,
        report_id,
        report_id_ma,
        reported_tcb,
        chip_id,
        committed_tcb,
        current_build,
        current_minor,
        current_major,
        committed_build,
        committed_minor,
        committed_major,
        launch_tcb,
        signature,
    ) = struct.unpack_from(f"<{SNP_REPORT_STRUCTURE}", attestation_bytes, 0)

    # Validate report was generated based on the provided report data
    # (i.e. This is the report we requested)
    assert report_data.rstrip(b"\x00").decode() == expected_report_data

    # Get the certificate chain to validate that the report is ultimately
    # endorsed by a trusted AMD certificate
    vcek_cert, ark_cert, root_cert = get_certificate_chain(certificate_chain)

    # Validate the VCEK certificate signed the report
    vcek_cert.public_key().verify(  # type: ignore
        encode_dss_signature(
            *(
                int.from_bytes(n, byteorder="little")
                for n in struct.unpack_from(SIGNATURE_STRUCTURE, signature)
            )
        ),
        attestation_bytes[: -len(signature)],
        ECDSA(SHA384()),  # type: ignore
    )  # type: ignore

    # Validate the ARK certificate signed the VCEK certificate
    assert cert_signed_other_cert(ark_cert, vcek_cert)

    # Validate the AMD root certificate signed the ARK certificate
    assert cert_signed_other_cert(root_cert, ark_cert)

    # Validate the AMD root certificate matches the known good value
    assert (
        root_cert.public_key().public_numbers()  # type: ignore
        == AMD_ROOT_PUBLIC_KEY.public_numbers()  # type: ignore
    )
