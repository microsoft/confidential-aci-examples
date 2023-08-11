# Encrypted Filesystem

This example builds on the [Key Release](../key_release/README.md) example by using the key to decrypt some memory containing a filesystem. This demonstrates how users with sensitive data can be crytographically assured that only their code can access their data.

It uses the EncFS sidecar from the [Confidential Sidecars Repository](https://github.com/microsoft/confidential-sidecar-containers). The sidecar will attempt to perform a key release based on the args provided via an environment variable, use the key to decrypt the filesystem, and then mount it in a volume which the primary container can then access.

### Delivering Encrypted Data to Container

There are a few possible ways to have the encrypted data in the container.

1. Embed data into image being deployed
2. Store data in the cloud and fetch it at runtime

This example does the latter, which requires a storage account capable of storing blob data. This example references a statically created container and adds blobs to it for each run. The code to create new containers can be found at [infra/deploy_storage_container.py](../../infra/deploy_storage_container.py).

At deployment time, [deploy_key_and_blob.py](deploy_key_and_blob.py) is run, which:

- Creates a key
- Creates a filesystem image
- Encrypts the filesystem image with the key
- Uploads the key to a managed HSM
- Uploads the encrypted filesystem image to the storage container

### Fetching and Decrypting the Data

The sidecar handles the key release, fetching the encrypted data, decrypting it, and mounting it. To do so, it needs to know among other details:

- The URL of the blob to download
- The ID of the key to release
- Where to mount the filesystem once decrypted

This information is passed as an environment variable `EncfsSideCarArgs` which is a base64 encoded JSON object, the details can be found in the [manifest](manifest.json). The infrastructure automatically base64 encodes any environment variables in the manifest which are provided as JSON objects.
