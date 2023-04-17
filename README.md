# Confidential ACI Examples

Example code and end to end test cases for confidential ACI. Contains infrastructure for deploying Confidential Azure Container Instances based on AMD SEV-SNP.

[![Tests](https://github.com/microsoft/confidential-aci-examples/actions/workflows/run_all.yml/badge.svg)](https://github.com/microsoft/confidential-aci-examples/actions/workflows/run_all.yml)

## Setup Development Environment

You can use Github Codespaces to create a fully ready to use development environment.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=616412316&machine=standardLinux32gb&devcontainer_path=.devcontainer%2Fdevcontainer.json&location=WestEurope)

> To checkout and setup manually, please refer to the [Dockerfile](.devcontainer/Dockerfile) and [.devcontainer](.devcontainer/devcontainer.json) to follow the setup process.

## Running Tests

If running in VS Code, open the testing view where all available tests are both runnable and debuggable. If not, run unittest as usual.

## Managing Test Infrastructure

While running tests directly will automatically manage the images and containers needed, it is also possible to use the infrastructure to manually manage these resources. Each management operation has a 1:1 mapping between running locally and in CI.

| Task                           | Implementation                                             | Run Locally                        | Run in CI                                                                         |
| ------------------------------ | ---------------------------------------------------------- | ---------------------------------- | --------------------------------------------------------------------------------- |
| Build and Push Container Image | Docker CLI                                                 | [tasks.json](.vscode/tasks.json)   | [build_and_push_images.yml](.github/workflows/build_and_push_images.yml)        |
| Generate ARM Template          | [generate_arm_template.py](infra/generate_arm_template.py) | [launch.json](.vscode/launch.json) | [\_generate_arm_template.yml](.github/workflows/_generate_arm_template.yml)       |
| Generate Security Policy       | Azure CLI                                                  | [tasks.json](.vscode/tasks.json)   | [\_generate_security_policy.yml](.github/workflows/_generate_security_policy.yml) |
| Deploy Container               | [deploy_container.py](infra/deploy_container.py)           | [launch.json](.vscode/launch.json) | [\_deploy_container.yml](.github/workflows/_deploy_container.yml)                 |
| Remove Container               | [remove_container.py](infra/remove_container.py)           | [launch.json](.vscode/launch.json) | [\_remove_container.yml](.github/workflows/_remove_container.yml)                 |

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
