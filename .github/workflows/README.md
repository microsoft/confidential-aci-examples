# Workflow Statuses

## Per Region Tests

Runs the simple server example 3 times in each region as an indicator for region health

[![Status of West Europe](https://github.com/microsoft/confidential-aci-examples/actions/workflows/status_westeurope.yml/badge.svg?branch=main)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/status_westeurope.yml)

[![Status of North Europe](https://github.com/microsoft/confidential-aci-examples/actions/workflows/status_northeurope.yml/badge.svg?branch=main)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/status_northeurope.yml)

#### Canary Region

[![Status of East US 2 EUAP](https://github.com/microsoft/confidential-aci-examples/actions/workflows/status_eastus2euap.yml/badge.svg?branch=main)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/status_eastus2euap.yml)

## Large Container Tests

Tests deploying larger containers in each region (4 core, 8/16GB memory)

[![Status of West Europe (Large Containers)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/status_westeurope_large_containers.yml/badge.svg?branch=main)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/status_westeurope_large_containers.yml)

[![Status of North Europe (Large Containers)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/status_northeurope_large_containers.yml/badge.svg?branch=main)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/status_northeurope_large_containers.yml)

#### Canary Region (Includes 16 and 32 core containers)

[![Status of East US 2 EUAP (Large Containers)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/status_eastus2euap_large_containers.yml/badge.svg?branch=main)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/status_eastus2euap_large_containers.yml)

## Uptime Tests

Tests which keep containers running the simple server example alive for 48 hours and checks that the container hasn't entered a failure state in that time

[![Uptime of Containers on West Europe](https://github.com/microsoft/confidential-aci-examples/actions/workflows/uptime_west_europe.yml/badge.svg)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/uptime_west_europe.yml)

#### Canary Region

[![Uptime of Containers on East US 2 EUAP](https://github.com/microsoft/confidential-aci-examples/actions/workflows/uptime_eastus2euap.yml/badge.svg)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/uptime_eastus2euap.yml)

## Sidecar Tests

Test which run against code which can change, in this case the [confidential-sidecar-containers](https://github.com/microsoft/confidential-sidecar-containers) repo. Examples whose sidecar is released to MCR also have a workflow targeting that.

### Attestation
[![Test Attestation](https://github.com/microsoft/confidential-aci-examples/actions/workflows/test_attestation.yml/badge.svg?event=schedule)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/test_attestation.yml)

#### Canary Region

[![Test Attestation (Canary)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/test_attestation_canary.yml/badge.svg?event=schedule)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/test_attestation_canary.yml)

### Key Release

[![Test Key Release](https://github.com/microsoft/confidential-aci-examples/actions/workflows/test_key_release.yml/badge.svg?event=schedule)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/test_key_release.yml)
[![Test Key Release (Latest)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/test_key_release_latest.yml/badge.svg?event=schedule)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/test_key_release_latest.yml)

#### Canary Region

[![Test Key Release (Canary)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/test_key_release_canary.yml/badge.svg?event=schedule)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/test_key_release_canary.yml)

### Encrypted Filesystem

[![Test Encrypted Filesystem](https://github.com/microsoft/confidential-aci-examples/actions/workflows/test_encrypted_filesystem.yml/badge.svg?event=schedule)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/test_encrypted_filesystem.yml)
[![Test Encrypted Filesystem (Latest)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/test_encrypted_filesystem_latest.yml/badge.svg?event=schedule)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/test_encrypted_filesystem_latest.yml)

#### Canary Region

[![Test Encrypted Filesystem (Canary)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/test_encrypted_filesystem_canary.yml/badge.svg?event=schedule)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/test_encrypted_filesystem_canary.yml)