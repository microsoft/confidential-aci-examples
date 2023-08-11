# Key Release

This example builds on the the [Attestation](../attestation/README.md) example by using the report as evidence to release a key from a Hardware Security Module (HSM) in Azure.

It uses the SKR (Secure Key Release) sidecar from the [Confidential Sidecars Repository](https://github.com/microsoft/confidential-sidecar-containers). This means that the primary container simply makes a request to the sidecar with inputs and it gets a key in return.

### 1. Create a Place to Store the Key

The sidecar can release keys from either Azure Key Vault (AKV) or Azure Managed HSM (mHSM), this example uses the latter.

Due to slow spin up time, this repository uses a single statically created mHSM, the code to do this can be found at [infra/deploy_hsm.py](../../infra/deploy_hsm.py).

Access is tightly controlled in mHSMs, the deployment script will also assign Administrator and Crypto User/Officer roles to the service principal and managed identity used by this repository's codespace.

### 2. Deploy the Key

Keys are deployed to the mHSM via an HTTP request to an endpoint owned by the mHSM. This example uses the preDeployScript feature of the infrastrucure to [deploy a key](deploy_key.py) to the mHSM just before the main ARM template is deployed.

The structure of the request is fairly readable in [keys.py](../../infra/keys.py). The key detail is the `release_policy` field. It is a base64 encoded string which uses simple logical statements to construct rules for when a key should be released. In this case, the key can be released either with a valid Azure Attestation token (which is only provided when the service validates an attestation) or with the raw attestation in which case it must contain a correct security policy digest among other things.

### 3. Release the Key

Keys are also released from a mHSM via an HTTP request, in this case the sidecar handles that part. All the primary container needs to do is make an HTTP request to the sidecar with the key ID it would like and the sidecar will get an attestation report, pass it to the Attestation service to validate and get a token, then pass the token to the mHSM which releases the key.
