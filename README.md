# Confidential ACI Examples

Example code and end to end test cases for confidential ACI. Contains infrastructure for deploying Confidential Azure Container Instances based on AMD SEV-SNP.

## Deploy ACIs

To use the ACI deployment infrastructure, open this repository in a codespace:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=616412316&machine=standardLinux32gb&devcontainer_path=.devcontainer%2Fdevcontainer.json&location=WestEurope)

From there, log into the Azure CLI, which can be done with the command `az login` (optionally with the `--use-device-code` flag).

Once logged in, running the [infra/deploy_aci.py](infra/deploy_aci.py) script with the appropriate command line arguments can both create and remove a Confidential Azure Container Instance to run examples against.

## Running the tests

To run the tests, we first need to provide some secrets and configuration to deploy an appropriate ACI and give it permission to use payloads from this (currently) private repo. To do this, run `infra/credentials.py` with appropriate arguments. Then the tests can pick up the config and secrets to deploy ACIs as needed.

```
python infra/credentials.py --subscription-id {YOUR_AZURE_SUBSCRIPTION_ID} --resource-group {YOUR_AZURE_RESOURCE_GROUP}  --username {YOUR_GITHUB_USERNAME} --pat {YOUR_GITHUB_PERSONAL_ACCESS_TOKEN}
```

Then run the tests as any other unittest based tests, VS code has good integration in it's testing tab

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
