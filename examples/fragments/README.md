# Examples using fragments

This directory contains examples demonstrating creation and usage of image attached fragments:

- [fragment-aci](fragment-aci/) contains an example for (plain) C-ACI
- [fragment-vn2](fragment-vn2/) contains an example for VN2 (using C-ACI via Virtual Node 2).  Not all region support fragments for VN2 yet.

In each example, the Makefile contains more detailed description in the top level comment.  Run `make` to generate the fragment, `make deploy` to deploy the workload, and `make verify` to verify the deployment has succeed and container output contains the expected string.
