Fragments
=========

## Policy

In Confidential Computing we are trying to make sure that only the code a customer intends to run can run. It is not a magic bullet. If that code is
faulty, has back doors, accidently listens on ports or is full of vulnerabilities it will not be fixed. The purpose is to prevent outside interference with
the workload from operators and the hosting platform. Typically the hypervisor has complete access to the memory space of a VM. With a TEE that is prevented
by hardware encryption of the VM's memory. With Confidential ACI there is also protection by constraining exactly what the workload is and can be asked to do.
This is what the policy encodes.

## Gatekeeping

TEEs provide an attestation report. This is used to prove that a workload is genuine and acceptable to some other party (aka the relying party)
which will decide whether or not to release secrets or confidential information to the workload. Without a gatekeeper of this sort the workload could be
an imposter, stealing the secret.

In Confidential ACI the gatekeeper will typically check that the initial measurement of the VM is correct and that a hash of the security policy is correct.
Any change to the UVM code or to the contents of the security policy, say to allow in a malicious version of a container, will be detected by the relying party
and it will not release the secret.

## Fragments

A fragment is a piece of security policy. It is contained within a COSE Sign1 wrapper so that it is signed and labelled.
Fragments are offered to a pod and if the security policy of the pod allows them they augment that policy. Thus a fragment might have rules to
allow a particular container to be admitted. This is a sort of late binding of policy. 

## Tools

There are some tools which can help create and understand COSE Sign1 files https://github.com/microsoft/cosesign1go/tree/main/cmd/sign1util
To put fragments into a container registry use the oras CLI - https://oras.land/

## Representation in a security policy

```json
fragments := [
    {"issuer": "did:x509:0:sha256:x24vHJbbv_HXxMacafr8jf8l7oQbNwCrM5jZbXzk9Lc::subject:CN:Test%20Leaf%20%28DO%20NOT%20TRUST%29", "feed": "acceuroperegistry.azurecr.io/infra:latest", "minimum_svn": "1.0.0", "includes": ["containers"]},
]
```
This rule means "accept the 'containers' section from any fragment signed by the given issuer and feed, SVN of at least 1.0.0".

Typical Confidential ACI workloads include a single fragment rule that allows in various ACI infrastructure sidecars that provide ACI features.

```json
fragments := [
  {
    "feed": "mcr.microsoft.com/aci/aci-cc-infra-fragment",
    "includes": [
      "containers",
      "fragments"
    ],
    "issuer": "did:x509:0:sha256:I__iuL25oXEVFdTP_aBLx_eT1RPHbCQ_ECBQfYZpt9s::eku:1.3.6.1.4.1.311.76.59.1.3",
    "minimum_svn": "1"
  }
]
```

Note that this rule allows the fragment to add both rules to white particular containers, via the usual Merkle tree root hashes, and to add new fragment rules.

## How fragments are chosen by the runtime.

There are three types of of fragment:

* Infrastructure
* Standalone
* Image attached

Infrastructure fragments, such as ```aci-cc-infra-fragment``` are automatically offered by the runtime.
Standalone fragments are similar but specified by the user.
Image attached fragments are automatically offered when found referring to a container image being loaded.

## What does "offered" mean?

The security policy, via a fragment rule as above, specifies what constitutes an acceptable fragment. This will typically represent a statement
of trust. "This workload trusts code signed by a particular party (issuer) with a particular label (feed)". The runtime will discover _potential_ fragments
and offer them to the policy engine (inside the TEE). The fragments must be well formed COSE_Sign1 documents - the issuer
**MUST** match the embedded certificate chain. The policy engine evaluates issuer/feed against the existing policy and if accepted it adds the new fragment of
policy.

## Typical use cases

### Allow serviceable infrastructure

ACI implements some feature by means of 'sidecars'. These are containers which run in the same utility VM as the customer workload. They can be updated by the
ACI team and that should not force a new security policy to be needed. This is achieved by having a fragment which whitelists those particular containers.

### Allow serviceable third party containers

Containerised applications can be composed of several parts, independently developed, packaged and released. The various SKR, Attestation and encrypted file system
containers at https://github.com/microsoft/confidential-sidecar-containers are examples. Each of these containers could/will (TBC) have an image attached fragment
containing appropriate policy to allow it to be used and signed by the controlling ACC team. Then a user could choose to use :latest rather than fixed tags and
not need to regenerate a security policy in sync with updates.

### Allow serviceable first party containers

Similarly, a customer could create a fragment for an in-house container and have a security policy that trusts that, thus avoiding direct coupling of the versions.

### Completely stable key release

If a security policy consists only of a fragment rule then the hash of that policy will be constant regardless of changes to the containers used. Image
attached or standalone fragments could provide the whole policy. Effectively any appropriately signed policy may be run.

# High level view

 TBC, short workflow alike using the mechanic below.


# Mechanics

## Signing certificate chain (aka ```chain.pem```)

    The ```issuer``` field is a DID:x509 (see https://github.com/microsoft/did-x509) identifier derived from the certificate chain used to sign the COSE Sign1 envelope. That certificate chain is embedded into the COSE Sign1 envelope as part of the headers.
    Thus the first step in publishing a fragment is to be able to sign things. The prefered option is to have a signing service capable to creating COSE Sign1 envelopes.
    Here I show the steps manually for the sake of clarity. An actual production system would have to use a proper secret store such as AKV to keep the signing certificates safe. 

cert.extensions.cfg contains:
```
basicConstraints=critical,CA:TRUE
keyUsage=digitalSignature,keyCertSign
```

See ```Makefile.certs``` which does all this for you with ```make -f Makefile.certs chain.pem```

```bash
# make the root private key
openssl ecparam -name secp384r1 -genkey -noout -out root.private.pem

# and the root certificate
openssl req -new -key root.private.pem -out root.cert.pem.tmp.csr -subj "/CN=Test Root CA (DO NOT TRUST)" -addext 'basicConstraints=critical,CA:TRUE' -addext 'keyUsage=digitalSignature,keyCertSign'
openssl x509 -req -days 365 -in root.cert.pem.tmp.csr -signkey root.private.pem -out root.cert.pem -CAcreateserial -extfile cert.extensions.cfg

# make the intermediate private key
openssl ecparam -name secp384r1 -genkey -noout -out intermediate.private.pem

# and the intermediate cert
openssl req -new -key intermediate.private.pem -out intermediate.cert.pem.tmp.csr -subj "/CN=Test Intermediate CA (DO NOT TRUST)" -addext 'basicConstraints=critical,CA:TRUE' -addext 'keyUsage=digitalSignature,keyCertSign'
openssl x509 -req -days 365 -in intermediate.cert.pem.tmp.csr -CA root.cert.pem -CAkey root.private.pem -out intermediate.cert.pem -CAcreateserial -extfile cert.extensions.cfg

# make the leaf private key
openssl ecparam -name secp384r1 -genkey -noout -out leaf.private.pem
# and the leaf cert
openssl req -new -key leaf.private.pem -out leaf.cert.pem.tmp.csr -subj "/CN=Test Leaf (DO NOT TRUST)"
# extendedkeyusage.cfg contains "extendedKeyUsage = 1.2.3.4.5.6.7.8.9.10.11"
openssl x509 -req -days 365 -in leaf.cert.pem.tmp.csr -CA intermediate.cert.pem -CAkey intermediate.private.pem -out leaf.cert.pem -CAcreateserial -extfile extendedkeyusage.cfg
# construct chain.pem by creating the individual public certs and concatenating them
openssl ec -in root.private.pem -pubout -out root.public.pem
openssl ec -in intermediate.private.pem -pubout -out intermediate.public.pem
openssl ec -in leaf.private.pem -pubout -out leaf.public.pem
cat `(for d in root.cert.pem intermediate.cert.pem leaf.cert.pem; do echo $d; done) | tac` >> chain.pem
```

In a proper system the root certificate will have a very long expiration date, 20 years or more. The leaf cert will have a reasonable life of perhaps a year.

## DID:x509 - stable identity for the issuer

A DID:x509 is a form of distributed ID that uses certificate pining. It essentially consists of a hash of the root certificate and some stable feature of the leaf certificate, such as subject (CN) or extended key usage (EKU) which the signing authority guarantees not to issue to anyone else. For example the ACI team uses an issuer of ```"did:x509:0:sha256:I__iuL25oXEVFdTP_aBLx_eT1RPHbCQ_ECBQfYZpt9s::eku:1.3.6.1.4.1.311.76.59.1.3"```. This is a combination of a sha256 hash of the root certificate (a proper, globaly trusted Microsoft root certificate) and the extended key use property of the leaf ```1.3.6.1.4.1.311.76.59.1.3```. It could be in terms of of other unique fields of the leaf, eg subject of ```CN:Test%20Leaf%20%28DO%20NOT%20TRUST%29```. They ```eku``` and ```subject``` part are known as the 'policy' of the DID:x509.

The tool ```sign1util`` can generate a did from a certificate chain, chain.pem in this example

```bash
sign1util.exe did-x509 -chain chain.pem
did:x509:0:sha256:830ZewoMr-OKTgNKQz4HlCfNM5P8x3NeZgwowSjziMc::subject:CN:Test%20Leaf%20%28DO%20NOT%20TRUST%29
```

or using an eku
```bash
sign1util.exe did-x509 -chain chain.pem -policy eku
did:x509:0:sha256:830ZewoMr-OKTgNKQz4HlCfNM5P8x3NeZgwowSjziMc::eku:1.2.3.4.5.6.7.8.9.10.11
```

or from a COSE Sign1 envelope
```bash
sign1util.exe did-x509 -in infra.rego.cose
checkCoseSign1 passed
iss: did:x509:0:sha256:x24vHJbbv_HXxMacafr8jf8l7oQbNwCrM5jZbXzk9Lc::subject:CN:Test%20Leaf%20%28DO%20NOT%20TRUST%29
feed: acceuroperegistry.azurecr.io/infra:latest
cty: application/unknown+rego
pubkey: MHYwEAYHKoZIzj0CAQYFK4EEACIDYgAELvNOZtioRshnHHC25sbHQ7mQJuvVkFJFR/qfRachJ0NIY7YyJJ7NGoHOOtgFU7KXRxlSoCYfNHoi/s6e5/frurZ5El8F2gcD+9aYDLYVcUEdSVl8+vf7LUoBLz6oiydC
pubcert: MIIBiTCCAQ8CFF68QgOtwdXzB3t9Afcr7CWs+FX7MAoGCCqGSM49BAMCMC4xLDAqBgNVBAMMI1Rlc3QgSW50ZXJtZWRpYXRlIENBIChETyBOT1QgVFJVU1QpMB4XDTI0MDMwNzE3MDIyOVoXDTI1MDMwNzE3MDIyOVowIzEhMB8GA1UEAwwYVGVzdCBMZWFmIChETyBOT1QgVFJVU1QpMHYwEAYHKoZIzj0CAQYFK4EEACIDYgAELvNOZtioRshnHHC25sbHQ7mQJuvVkFJFR/qfRachJ0NIY7YyJJ7NGoHOOtgFU7KXRxlSoCYfNHoi/s6e5/frurZ5El8F2gcD+9aYDLYVcUEdSVl8+vf7LUoBLz6oiydCMAoGCCqGSM49BAMCA2gAMGUCMFR4CXfH/VHmteSB83g9dNtaYMuRfM61zREDBQsTKjn1XQiL3LqVsmQoYcrPLTRGlAIxAPV+HF7/woeMqY7naN0iodPJJy4Rf2s9j7sFZxuCKxpu7V4FcgniOPZkocHfzXFzOA==       
payload:
<snip the rego>
```

## Policy generation

See also https://github.com/Azure/azure-cli-extensions/blob/main/src/confcom/azext_confcom/README.md

There are two forms of policy, the base policy that is provided directly at pod startup time and late bound fragments.

```az confcom acipolicygen --image alpine:latest --outraw```
will generate the policy that allows a simple alpine container to run with defaults








