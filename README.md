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

### [Simple Server](examples/simple_server/README.md)

Hello world server running in a confidential container.

### [Simple Sidecar](examples/simple_sidecar/README.md)

Deploys two containers in the same container group and demostrates communication between the two.

### [Remote Image](examples/remote_image/README.md)

Simplest possible example to demonstrate how resources are managed by this repo.

### [Attestation](examples/attestation/README.md)

Fetches and validates an SNP Attestation report, locally as well as using a sidecar.

## Setup Development Environment

You can use Github Codespaces to create a fully ready to use development environment.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=616412316&machine=standardLinux32gb&devcontainer_path=.devcontainer%2Fdevcontainer.json&location=WestEurope)

> **CREDENTIALS:** If you do not have write permissions on this project or you checkout manually i.e. without using Codespaces, you will need to provide your own credentials by modifying the [Environment file](env) and re-running [setup.sh](setup.sh)

> **MANUAL SETUP:** To checkout and setup manually, please refer to the [Dockerfile](.devcontainer/Dockerfile) and [.devcontainer](.devcontainer/devcontainer.json) to follow the setup process.

## Running Tests

If running in VS Code, open the testing view where all available examples are both runnable and debuggable. If not, run unittest as usual.

### **[EXPERIMENTAL] Running examples against Container Platform**

You can currently run the following examples against Container Platform.

- Simple Server
- Remote Image

To do so, log into Azure with an account which has access to both the Azure DevOps repository for ContainerPlatform, and the Atlas Image on which it runs.

## Managing Test Infrastructure

While running examples directly will automatically manage the images and containers needed, it is also possible to use the infrastructure to manually manage these resources. Each management operation can be run via VS Code's [launch configurations](.vscode/launch.json)

| Task                           | Implementation                                                       | Run in CI                                                                      |
| ------------------------------ | -------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Build and Push Container Image | [build_and_push_images.py](infra/build_and_push_images.py)           | [build_and_push_images.yml](.github/workflows/build_and_push_images.yml)       |
| Generate Security Policy       | [generate_security_policy.py](infra/generate_security_policy.py)     | [generate_security_policy.yml](.github/workflows/generate_security_policy.yml) |
| Generate ARM Template          | [generate_arm_template.py](infra/container/generate_arm_template.py) | [generate_arm_template.yml](.github/workflows/generate_arm_template.yml)       |
| Deploy Container               | [deploy_arm_template.py](infra/deploy_arm_template.py)               | [deploy_arm_template.yml](.github/workflows/deploy_arm_template.yml)           |
| Remove Container               | [delete_deployment.py](infra/delete_deployment.py)                   | [delete_deployment.yml](.github/workflows/delete_deployment.yml)               |

## Adding New Tests

- Create a new directory under examples with the name of your new test
- Add a manifest.json file to the new directory and fill in the required fields
  - At least one container image is needed, so create a Dockerfile and mention it in the manifest
  - Manifest files are automatically validated if running in codespaces, otherwise refer to the schema in [.devcontainer.json](.devcontainer/devcontainer.json)
- Add python code which uses the unittest module to declare tests, inherit [TestCase](infra/test_case.py) to deploy containers during the setup of tests.

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
