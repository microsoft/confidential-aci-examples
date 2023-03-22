# Confidential ACI Examples

Example code and end to end test cases for confidential ACI. Contains infrastructure for deploying Confidential Azure Container Instances based on AMD SEV-SNP.



## Setup Development Envrionment

1. Open the codespace (or checkout manually, checking the [.devcontainer](devcontainer) for dependency information)

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=616412316&machine=standardLinux32gb&devcontainer_path=.devcontainer%2Fdevcontainer.json&location=WestEurope)

2. Log into Azure CLI

```
az login
```

If running in a browser, it might be easier to use:

```
az login --use-device-code
```

3. Set credentials for Azure (If using VS Code, there is a launch config for this)

```
python infra/credentials.py \
    --subscription-id {YOUR_AZURE_SUBSCRIPTION_ID} \
    --resource-group {YOUR_AZURE_RESOURCE_GROUP} \
    --registry-password {YOUR_CONTAINER_REGISTRY_PASSWORD}
```

From here, all infrastructre functionality should be available to use. If using VS code, there are [Run/Debug configurations](.vscode/launch.json) for managing images and containers.

## Running Tests

If running in VS Code, opening any test such as [simple_server.py](tests/simple_server.py) presents the testing view where each test can be run or debugged individually.

Tests handle deploying and removing ACIs to test against.

----------------

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
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
