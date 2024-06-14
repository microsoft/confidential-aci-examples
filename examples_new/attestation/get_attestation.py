# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse
import ctypes
import struct
import os

from fcntl import ioctl

# Data structures are based on SEV-SNP Firmware ABI Specification
# https://www.amd.com/en/support/tech-docs/sev-secure-nested-paging-firmware-abi-specification

# Report Data to pass into Attestation
REPORT_DATA_SIZE = 64

# MSG_REPORT_REQ (Table 20)
REPORT_REQ_STRUCTURE = "".join(
    [
        "<",  # Little Endian
        f"{REPORT_DATA_SIZE}s",  # Report Data
        "I",  # VMPL
        "3x",  # -----
        "B",  # Key Selection
        "24x",  # -----
    ]
)
REPORT_REQ_SIZE = struct.calcsize(REPORT_REQ_STRUCTURE)
VMPL = 0
KEY_SEL = 0

# SEV-SNP Guest Request (sev-snp driver include/uapi/linux/psp-sev-guest.h)
SNP_GUEST_REQ_STRUCTURE = "".join(
    [
        "<",  # Little Endian
        "B",  # Request Type
        "B",  # Response Type
        "B",  # Guest Message Version
        "x",  # -----
        "H",  # Request Size
        "2x",  # -----
        "Q",  # Request Pointer
        "H",  # Response Size
        "6x",  # -----
        "Q",  # Response Pointer
        "4x",  # -----
        "I",  # Guest Error
    ]
)
SNP_GUEST_REQ_SIZE = struct.calcsize(SNP_GUEST_REQ_STRUCTURE)
REPORT_REQ_CODE = 5
REPORT_RSP_CODE = 6
SNP_GUEST_MSG_VERSION = 1
GUEST_ERROR = 0

# IOCTL (sev-snp driver include/uapi/linux/psp-sev-guest.h)
SNP_GUEST_MSG_IOCTL_PATH = "/dev/sev"
SNP_GUEST_MSG_IOCTL_CODE = 3223868161

SIGNATURE_STRUCTURE = "".join(
    [
        "72s",  # R Component
        "72s",  # S Component
        "368x",  # -----
    ]
)

# SNP Report (Table 21)
SNP_REPORT_STRUCTURE = "".join(
    [
        "I",  # Version
        "I",  # Guest SVN
        "Q",  # Policy
        "16s",  # Family ID
        "16s",  # Image ID
        "I",  # VMPL
        "I",  # Signature Algorithm
        "Q",  # Current TCB
        "Q",  # Platform Info
        "I",  # Signing Key/Mask Chip Key/Author Key
        "4x",  # -----
        f"{REPORT_DATA_SIZE}s",  # Report Data
        "48s",  # Measurement
        "32s",  # Host Data
        "48s",  # ID Key Digest
        "48s",  # Author Key Digest
        "32s",  # Report ID
        "32s",  # Report ID MAA
        "Q",  # Reported TCB
        "24x",  # -----
        "64s",  # Chip ID
        "Q",  # Committed TCB
        "B",  # Current Build
        "B",  # Current Minor
        "B",  # Current Major
        "x",  # -----
        "B",  # Committed Build
        "B",  # Committed Minor
        "B",  # Committed Major
        "x",  # -----
        "Q",  # Launch TCB
        "168x",  # -----
        "512s",  # Signature
    ]
)
SNP_REPORT_SIZE = struct.calcsize(SNP_REPORT_STRUCTURE)

# MSG_REPORT_RSP (Table 23)
REPORT_RSP_STRUCTURE = "".join(
    [
        "<",  # Little Endian
        "I",  # Status
        "I",  # Report Size
        "24x",  # -----
        SNP_REPORT_STRUCTURE,
        "64x",  # padding to the size of SEV_SNP_REPORT_RSP_BUF_SZ
    ]
)
REPORT_RSP_SIZE = struct.calcsize(REPORT_RSP_STRUCTURE)


def get_attestation_report(report_data: bytes):
    # Create MSG_REPORT_REQ
    report_req = bytearray(REPORT_REQ_SIZE)
    struct.pack_into(
        REPORT_REQ_STRUCTURE,
        report_req,
        0,
        report_data[0:64],
        VMPL,
        KEY_SEL,
    )

    # Create blank MSG_REPORT_RSP to be populated by the IOCTL call
    report_rsp = bytearray(REPORT_RSP_SIZE)

    # Create the SEV-SNP Guest Request
    guest_req = bytearray(SNP_GUEST_REQ_SIZE)
    struct.pack_into(
        SNP_GUEST_REQ_STRUCTURE,
        guest_req,
        0,
        REPORT_REQ_CODE,
        REPORT_RSP_CODE,
        SNP_GUEST_MSG_VERSION,
        REPORT_REQ_SIZE,
        ctypes.addressof(ctypes.c_byte.from_buffer(report_req)),
        REPORT_RSP_SIZE,
        ctypes.addressof(ctypes.c_byte.from_buffer(report_rsp)),
        GUEST_ERROR,
    )

    # Call the IOCTL
    fd = os.open(SNP_GUEST_MSG_IOCTL_PATH, os.O_RDWR | os.O_CLOEXEC)
    ioctl(fd, SNP_GUEST_MSG_IOCTL_CODE, bytes(guest_req))

    status, _report_size, *report = struct.unpack_from(
        REPORT_RSP_STRUCTURE, report_rsp, 0
    )
    if status != 0:
        raise RuntimeError(f"Report Generation Failed: {status}")

    return struct.pack(f"<{SNP_REPORT_STRUCTURE}", *report)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-data", type=str, default="")
    args = parser.parse_args()

    print(
        get_attestation_report(
            report_data=struct.pack(
                f"<{REPORT_DATA_SIZE}s",
                args.report_data.encode("utf-8"),
            ),
        )
    )
