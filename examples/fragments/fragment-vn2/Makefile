# Confidential VN2 demo: image-attached CCE policy fragments (VN2)
#
# This demo shows how an image attached fragment lets a stable top level policy
# authorise different versions of an image. This deployment uses VN2.
#
# We build two different workload images (A and B), and each image is pushed to
# the registry with their fragments attached via ORAS. Because both fragments
# are signed by the same issuer and uses the same "feed", either one is allowed
# by the top level policy.
#
# We render (via envsubst) both pods from a template into a single manifest that
# differs only by name + image, let confcom generate + inject the top level policy
# into each, and show the two injected policies are byte-for-byte identical. The
# workload image layer hashes only appear in the fragments, not the top level policy.
#
# Flow (just run `make && make deploy && make verify`):
#    tools     download oras + sign1util if not already on PATH
#    certs     create a demo signing cert chain
#    login     az acr login
#    images    build + push workload A and workload B
#    fragments For each image, generate a fragment, sign with sign1util, attach
#              with oras, and emit its import rule
#    yaml      render both pods + inject one top level policy into each (in place)
#    deploy    apply the manifest
#    verify    check both pods started
#
# Requirements you must provide yourself (not installed here):
#    - Azure CLI + the `confcom` extension  (az extension add --name confcom)
#    - docker (with buildx), kubectl
#    - An AKS cluster with VN2 installed, and your kubeconfig pointing at it
#    - An Azure Container Registry you can push to

# Configuration (override on the command line or via the environment)
REGISTRY         ?= cacidashboardaci.azurecr.io
REPO_BASE        ?= fragment-vn2
TAG              ?= demo
DEPLOYMENT_NAME  ?= fragment-vn2-demo

# Derived values
REGISTRY_NAME    := $(firstword $(subst ., ,$(REGISTRY)))
WORKLOAD_A_IMAGE := $(REGISTRY)/$(REPO_BASE)/workload-a:$(TAG)
WORKLOAD_B_IMAGE := $(REGISTRY)/$(REPO_BASE)/workload-b:$(TAG)

# The "feed" is the stable name a policy uses to refer to a fragment. Both
# workloads publish under this single feed, so one import rule covers both.
FEED             := $(REGISTRY)/$(REPO_BASE)

# Demo signing material produced by certs/create_certchain.sh
CHAIN := certs/intermediateCA/certs/www.contoso.com.chain.cert.pem
KEY   := certs/intermediateCA/private/ec_p384_private.pem

# Tools we download on demand go here (added to PATH for recipes)
BIN := $(CURDIR)/bin
export PATH := $(BIN):$(PATH)
ORAS_VERSION      := 1.2.2
SIGN1UTIL_VERSION := 1.4.0

.PHONY: all tools certs login images fragments yaml deploy verify remove clean

all: yaml

# tools: install oras and sign1util only if they aren't already available.
tools:
	@command -v oras       >/dev/null 2>&1 || $(MAKE) --no-print-directory $(BIN)/oras
	@command -v sign1util  >/dev/null 2>&1 || $(MAKE) --no-print-directory $(BIN)/sign1util

$(BIN)/oras:
	mkdir -p $(BIN)
	curl -fsSL https://github.com/oras-project/oras/releases/download/v$(ORAS_VERSION)/oras_$(ORAS_VERSION)_linux_amd64.tar.gz \
		| tar -xz -C $(BIN) oras
	chmod +x $(BIN)/oras

$(BIN)/sign1util:
	mkdir -p $(BIN)
	curl -fsSL -o $(BIN)/sign1util \
		https://github.com/microsoft/cosesign1go/releases/download/v$(SIGN1UTIL_VERSION)/sign1util
	chmod +x $(BIN)/sign1util

# certs: one-off creation of a demo root/intermediate cert chain used to sign
# fragments. In production you would use your own signing key + certificate.
certs:
	@test -f $(KEY) || ./certs/create_certchain.sh

login:
	az acr login --name $(REGISTRY_NAME)

# images: --provenance=false --sbom=false keeps the pushed image a single
# manifest so a fragment can be attached to it directly with oras.
images: login
	docker buildx build --provenance=false --sbom=false -t $(WORKLOAD_A_IMAGE) containers/workload-a
	docker push $(WORKLOAD_A_IMAGE)
	docker buildx build --provenance=false --sbom=false -t $(WORKLOAD_B_IMAGE) containers/workload-b
	docker push $(WORKLOAD_B_IMAGE)

# fragments: for each workload image we
#   1. generate an unsigned fragment (az confcom acifragmentgen, no signing args)
#   2. sign it explicitly with sign1util
#   3. attach the signed fragment to the image with oras
#   4. emit the fragment's import rule
#
# Note: `az confcom acifragmentgen` can do all of steps 1-3 in a single command
# if you pass the signing key/chain and an upload target, e.g.:
#
#     az confcom acifragmentgen \
#         --input workload-a-config.json --svn 1 --namespace contoso \
#         --chain $(CHAIN) --key $(KEY) \
#         --upload-fragment --image-target $(WORKLOAD_A_IMAGE)
#
# We deliberately split it out below to show each step (and to sign with
# sign1util directly rather than letting confcom drive the signing).
fragments: certs tools images
	rm -f import-a.json import-b.json fragment_import_rules.json
	@set -e; \
	for pair in "a $(WORKLOAD_A_IMAGE)" "b $(WORKLOAD_B_IMAGE)"; do \
	  set -- $$pair; suffix=$$1; image=$$2; \
	  echo "### Building fragment for workload $$suffix ($$image)"; \
	  WORKLOAD_IMAGE=$$image envsubst '$$WORKLOAD_IMAGE' < workload_config.json.template > workload-$$suffix-config.json; \
	  echo "# 1. generate the unsigned fragment rego"; \
	  az confcom acifragmentgen \
	      --input workload-$$suffix-config.json \
	      --svn 1 --namespace contoso \
	      --no-print --output-filename workload-$$suffix-fragment; \
	  echo "# 2. sign it with sign1util"; \
	  issuer=$$(sign1util did-x509 -chain $(CHAIN) -policy CN); \
	  sign1util create -algo ES384 -chain $(CHAIN) -key $(KEY) \
	      -claims workload-$$suffix-fragment.rego -out workload-$$suffix-fragment.rego.cose \
	      -salt zero -feed $(FEED) -content-type application/unknown+rego -issuer $$issuer; \
	  echo "# 3. attach the signed fragment to the image"; \
	  oras attach $$image \
	      --artifact-type application/x-ms-ccepolicy-frag \
		  --platform linux/amd64 \
	      workload-$$suffix-fragment.rego.cose:application/cose-x509+rego; \
	  echo "# 4. export the fragment's import rule (input for top level policy generation)"; \
	  az confcom acifragmentgen --generate-import \
	      -p workload-$$suffix-fragment.rego.cose --minimum-svn 1 \
	      --fragments-json import-$$suffix.json; \
	done
	@echo "### The two import rules must be identical (same feed + issuer + svn)"
	cmp import-a.json import-b.json
	cp import-a.json fragment_import_rules.json
	@echo
	@echo "--- fragment for workload a ---"
	@cat workload-a-fragment.rego
	@echo
	@echo "--- fragment for workload b ---"
	@cat workload-b-fragment.rego
	@echo
	@echo "--- fragment import rule ---"
	@cat fragment_import_rules.json
	@echo

# yaml: render both pods (differing only by name + image) into one
# multi-document manifest, then let confcom generate the top level policy and add it
# into each pod's annotation. Omitting --outraw* makes confcom modify the yaml
# in place. Because each workload is covered by its attached fragment, their
# definitions do not appear in the top level policy, which is why both pods end up
# with an identical top level policy.
#
# The top level policy does still contain the "pause" container which is required in
# all top level policies.
yaml: fragments
	POD_NAME=$(DEPLOYMENT_NAME)-a IMAGE=$(WORKLOAD_A_IMAGE) \
	    envsubst '$$POD_NAME $$IMAGE' < deployment.yaml.template > deployment.yaml
	echo '---' >> deployment.yaml
	POD_NAME=$(DEPLOYMENT_NAME)-b IMAGE=$(WORKLOAD_B_IMAGE) \
	    envsubst '$$POD_NAME $$IMAGE' < deployment.yaml.template >> deployment.yaml
	az confcom acipolicygen --virtual-node-yaml deployment.yaml \
	    --include-fragments --fragments-json fragment_import_rules.json
	@a=$$(grep 'ccepolicy' deployment.yaml | sed -n 1p | awk -F': ' '{print $$2}'); \
	 b=$$(grep 'ccepolicy' deployment.yaml | sed -n 2p | awk -F': ' '{print $$2}'); \
	 if [ "$$a" = "$$b" ]; then \
	   echo "OK: both pods share an identical top level policy (fragment-based)"; \
	 else echo "ERROR: the two injected policies differ" >&2; exit 1; fi
	@echo "--- top level policy (decoded) ---"
	@grep 'ccepolicy' deployment.yaml | sed -n 1p | awk -F': ' '{print $$2}' | base64 -d
	@echo

# deploy
deploy: yaml
	kubectl apply -f deployment.yaml

verify:
	@set -e; \
	for suffix in a b; do \
	  name=$(DEPLOYMENT_NAME)-$$suffix; \
	  echo "=== waiting for deployment $$name ==="; \
	  kubectl rollout status deployment/$$name --timeout=300s; \
	  kubectl logs deployment/$$name | tee logs-$$name.txt; \
	  grep -q "Workload container started" logs-$$name.txt; \
	done
	@echo "Both workloads started under the same top level policy -- fragments work."

remove:
	-kubectl delete -f deployment.yaml --ignore-not-found

clean:
	rm -f workload-*-config.json *.rego *.rego.cose import-*.json fragment_import_rules.json \
	      deployment.yaml logs-*.txt
	rm -rf bin certs/rootCA certs/intermediateCA
