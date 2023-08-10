# Confidential ACI Examples

Example code and end to end test cases for confidential ACI. Contains infrastructure for deploying Confidential Azure Container Instances based on AMD SEV-SNP.

[![Status of East US 2 EUAP](https://github.com/microsoft/confidential-aci-examples/actions/workflows/status_eastus2euap.yml/badge.svg?branch=main)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/status_eastus2euap.yml)
[![Status of West Europe](https://github.com/microsoft/confidential-aci-examples/actions/workflows/status_westeurope.yml/badge.svg?branch=main)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/status_westeurope.yml)
[![Status of North Europe](https://github.com/microsoft/confidential-aci-examples/actions/workflows/status_northeurope.yml/badge.svg?branch=main)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/status_northeurope.yml)

[![Uptime of Containers on East US 2 EUAP](https://github.com/microsoft/confidential-aci-examples/actions/workflows/uptime_eastus2euap.yml/badge.svg)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/uptime_eastus2euap.yml)
[![Uptime of Containers on West Europe](https://github.com/microsoft/confidential-aci-examples/actions/workflows/uptime_west_europe.yml/badge.svg)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/uptime_west_europe.yml)

[![Attestation Test Daily](https://github.com/microsoft/confidential-aci-examples/actions/workflows/test_attestation.yml/badge.svg?event=schedule)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/test_attestation.yml)
[![Key Release Test Daily](https://github.com/microsoft/confidential-aci-examples/actions/workflows/test_key_release.yml/badge.svg?event=schedule)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/test_key_release.yml)
[![Key Release Test Daily (Sidecar Repo Main Branch)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/test_key_release_daily.yml/badge.svg?event=schedule)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/test_key_release_daily.yml)

## Examples

### [Attestation](examples/attestation/README.md)

Fetches and validates an SNP Attestation report, locally as well as using the [Attestation sidecar](https://github.com/microsoft/confidential-sidecar-containers).

### [Encrypted Filesystem](examples/encrypted_filesystem)

Uses the [Encrypted Filesystem sidecar](https://github.com/microsoft/confidential-sidecar-containers) to demonstrate using attestation to perform a secure key release from an Azure HSM which is then used to decrypt a simple filesystem.

### [Key Release](examples/key_release)

Uses attestation to perform a secure key release from an Azure HSM.

### [Remote Image](examples/remote_image)

Simplest possible example to demonstrate how resources are managed by this repo.

### [Simple Server](examples/simple_server)

Hello world server running in a confidential container.

### [Simple Sidecar](examples/simple_sidecar)

Deploys two containers in the same container group and demostrates communication between the two.

## How to Run Examples

There are three main ways to run examples:

### 1. Github Actions

Every example has a corresponding github action which runs against all security policies in the examples manifest as well as one generated by the ACI Policy Generation tool.

See all workflows [here](https://github.com/microsoft/confidential-aci-examples/actions/workflows).

### 2. Whole Tests Locally

The simplest way to run the tests locally is to use Github Codespaces.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=616412316&machine=standardLinux32gb&devcontainer_path=.devcontainer%2Fdevcontainer.json&location=WestEurope)

This will set up a full development environment with everything needed to run examples.

> **CREDENTIALS:** If you do not have write permissions on this project or you checkout manually i.e. without using Codespaces, you will need to provide your own credentials by modifying the [Environment file](env) and re-running [setup.sh](setup.sh)

> **MANUAL SETUP:** To checkout and setup manually, please refer to the [Dockerfile](.devcontainer/Dockerfile) and [.devcontainer](.devcontainer/devcontainer.json) to follow the setup process.

Then you can open VS Code's testing view, where examples can be run with or without a debugger.

<img src="docs/testing_view.png" alt="VS Codes Testing View" width=400px>

### 3. Locally Step by Step

If a particular step of an example needs debugging, they can be run manually through [VS Codes Run and Debug View](https://code.visualstudio.com/docs/editor/debugging#_launch-configurations). Most examples follow these steps:

1. Build and Push Images
2. Generate ARM Template for ACI deployment
3. Generate a security policy based on that ARM template (optional)
4. Add a security policy to the ARM template
5. Deploy ARM Template

<img src="docs/debug_view.png" alt="VS Codes Testing View" width=400px>

Once the deployment is complete, you can run an example via unittest against the static deployment by setting the DEPLOYMENT_NAME environment variable in the [env file](env).

### [EXPERIMENTAL] Running examples against Container Platform

You can currently run the following examples against Container Platform.

- Simple Server
- Remote Image

To do so, log into Azure with an account which has access to both the Azure DevOps repository for ContainerPlatform, and the Atlas Image on which it runs. To do this, either set the environment variable BACKEND=VM, or when running each step manually, use the following steps:

1. Build and Push Images
2. Generate VM ARM Template
3. Deploy Container Platform
4. Run Container Platform

## How to Add New Examples

### 1. Create a new directory under examples with the name of your new test

- Must contain an \_\_init\_\_.py file.

### 2. Add a manifest file

- Must be directly under your new directory and named `manifest.json`
- At least one container image is needed, so create a Dockerfile and mention it in the manifest
- Manifest files are automatically validated if running in codespaces, otherwise refer to the schema in [.devcontainer.json](.devcontainer/devcontainer.json)

### 3. Add client side tests

- Add python code which uses the unittest module to declare tests, inherit [TestCase](infra/test_case.py) to deploy containers during the setup of tests.

### 4. Add a Github Actions workflow

- Must contain two jobs
  - One which generates a unique ID for the run and uploads a version of the test manifest which has been run through [resolve_manifest_variables.py](infra/resolve_manifest_variables.py)
  - One which depends on the first and calls [run_test.yml](.github/workflows/run_test.yml) with your unique ID and the test name

---

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
