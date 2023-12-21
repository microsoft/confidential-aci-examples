# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from infra.workload_identity import setup_federated_identity, enable_workload_identity_on_cluster


if __name__ == "__main__":
    enable_workload_identity_on_cluster()
    setup_federated_identity()