#!/bin/bash

version="0.1.17"
gh release download $version -R microsoft/confidential-aci-testing
pip install c-aci-testing*.tar.gz
rm c-aci-testing*.tar.gz