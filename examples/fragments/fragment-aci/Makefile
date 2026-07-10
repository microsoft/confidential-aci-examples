# Confidential ACI demo: image-attached CCE policy fragments (ACI)
#
# This demo shows how an image attached fragment lets a stable main policy
# authorise different versions of an image. This deployment uses ACI (without
# VN2).
#
# We build two different workload images (A and B), and each image is pushed to
# the registry with their fragments attached via ORAS. Because both fragments
# are signed by the same issuer and uses the same "feed", either one is allowed
# by the main policy.
#
# We then deploy that same main policy twice, once with image A and once with
# image B, and both succeed. The workload image layer hashes only appear in the
# fragments, not the main policy.
#
# Flow (just run `make && make deploy && make verify`):
#    tools     download oras + sign1util if not already on PATH
#    certs     create a demo signing cert chain
#    login     az acr login
#    images    build + push workload A and workload B
#    fragments For each image, generate a fragment, sign with sign1util, attach
#              with oras, and emit its import rule
#    policy    generate one main policy that imports the fragment
#    deploy    deploy that same policy with image A, then with image B
#    verify    check both container groups started
#
# Requirements you must provide yourself (not installed here):
#    - Azure CLI + the `confcom` extension  (az extension add --name confcom)
#    - docker (with buildx)
#    - An Azure Container Registry and a user-assigned managed identity that
#      can pull from it, in the target resource group.

# Configuration (override on the command line or via the environment)
REGISTRY         ?= cacidashboardaci.azurecr.io
REPO_BASE        ?= fragment-aci
TAG              ?= demo
LOCATION         ?= westeurope
RESOURCE_GROUP   ?= c-aci-dashboard
MANAGED_IDENTITY ?= cacidashboard-$(LOCATION)
DEPLOYMENT_NAME  ?= fragment-aci-demo

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

.PHONY: all tools certs login images fragments params policy deploy verify remove clean

all: policy

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
	      workload-$$suffix-fragment.rego.cose:application/cose-x509+rego; \
	  echo "# 4. export the fragment's import rule (input for main policy generation)"; \
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

# ARM parameter files that differ only in name + image.
params:
	CG_NAME=$(DEPLOYMENT_NAME)-a LOCATION=$(LOCATION) REGISTRY=$(REGISTRY) \
	  IMAGE=$(WORKLOAD_A_IMAGE) MANAGED_IDENTITY=$(MANAGED_IDENTITY) \
	  envsubst < deployment.parameters.json.template > deployment.parameters.a.json
	CG_NAME=$(DEPLOYMENT_NAME)-b LOCATION=$(LOCATION) REGISTRY=$(REGISTRY) \
	  IMAGE=$(WORKLOAD_B_IMAGE) MANAGED_IDENTITY=$(MANAGED_IDENTITY) \
	  envsubst < deployment.parameters.json.template > deployment.parameters.b.json

# policy: generate one main policy and inject it into the ARM template. Running
# acipolicygen without --outraw* injects the base64 policy directly into the
# (blank) ccePolicy field. Because each workload is covered by its attached
# fragment, their definitions do not appear in the main policy, which is why the
# same policy authorises both images.
policy: fragments params login
	cp deployment.arm.json deployment.policy.json
	az confcom acipolicygen \
	    -a deployment.policy.json \
	    -p deployment.parameters.a.json \
	    --include-fragments --fragments-json fragment_import_rules.json
	@echo "--- main policy (decoded) ---"
	@python3 -c "import json, base64; print(base64.b64decode(json.load(open('deployment.policy.json'))['resources'][0]['properties']['confidentialComputeProperties']['ccePolicy']).decode())"
	@echo

# deploy: deploy the same policy (deployment.policy.json) twice, changing only
# the image parameter. Both succeed because each image carries its own fragment.
deploy: policy params
	az deployment group create --name $(DEPLOYMENT_NAME)-a \
	    --resource-group $(RESOURCE_GROUP) \
	    --template-file deployment.policy.json \
	    --parameters @deployment.parameters.a.json
	az deployment group create --name $(DEPLOYMENT_NAME)-b \
	    --resource-group $(RESOURCE_GROUP) \
	    --template-file deployment.policy.json \
	    --parameters @deployment.parameters.b.json

verify:
	@set -e; \
	for suffix in a b; do \
	  name=$(DEPLOYMENT_NAME)-$$suffix; \
	  echo "=== waiting for $$name to log its startup ==="; \
	  for i in $$(seq 1 30); do \
	    az container logs --resource-group $(RESOURCE_GROUP) --name $$name \
	        --container-name workloadcontainer > logs-$$name.txt 2>/dev/null || true; \
	    grep -q "Workload container started" logs-$$name.txt && break; \
	    sleep 10; \
	  done; \
	  cat logs-$$name.txt; \
	  grep -q "Workload container started" logs-$$name.txt; \
	done
	@echo "Both workloads started under the same main policy -- fragments work."

remove:
	-az container delete --yes --resource-group $(RESOURCE_GROUP) --name $(DEPLOYMENT_NAME)-a
	-az container delete --yes --resource-group $(RESOURCE_GROUP) --name $(DEPLOYMENT_NAME)-b

clean:
	rm -f workload-*-config.json *.rego *.rego.cose import-*.json fragment_import_rules.json \
	      deployment.policy.json deployment.parameters.*.json logs-*.txt
	rm -rf bin certs/rootCA certs/intermediateCA
