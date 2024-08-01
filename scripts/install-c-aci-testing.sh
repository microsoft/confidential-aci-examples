#!/bin/bash

version="1.0.3"
gh release download $version -R microsoft/confidential-aci-testing
pip install c_aci_testing*.tar.gz
rm c_aci_testing*.tar.gz