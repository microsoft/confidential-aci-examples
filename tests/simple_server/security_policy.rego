package policy

import future.keywords.every
import future.keywords.in

api_svn := "0.10.0"
framework_svn := "0.1.0"

fragments := [
  {
    "feed": "mcr.microsoft.com/aci/aci-cc-infra-fragment",
    "includes": [
      "containers"
    ],
    "issuer": "did:x509:0:sha256:I__iuL25oXEVFdTP_aBLx_eT1RPHbCQ_ECBQfYZpt9s::eku:1.3.6.1.4.1.311.76.59.1.3",
    "minimum_svn": "1.0.0"
  }
]

containers := [{"allow_elevated":true,"allow_stdio_access":true,"command":["python","payload.py"],"env_rules":[{"pattern":"PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin","required":false,"strategy":"string"},{"pattern":"LANG=C.UTF-8","required":false,"strategy":"string"},{"pattern":"GPG_KEY=A035C8C19219BA821ECEA86B64E628F8D684696D","required":false,"strategy":"string"},{"pattern":"PYTHON_VERSION=3.11.2","required":false,"strategy":"string"},{"pattern":"PYTHON_PIP_VERSION=22.3.1","required":false,"strategy":"string"},{"pattern":"PYTHON_SETUPTOOLS_VERSION=65.5.1","required":false,"strategy":"string"},{"pattern":"PYTHON_GET_PIP_URL=https://github.com/pypa/get-pip/raw/d5cb0afaf23b8520f1bbcfed521017b4a95f5c01/public/get-pip.py","required":false,"strategy":"string"},{"pattern":"PYTHON_GET_PIP_SHA256=394be00f13fa1b9aaa47e911bdb59a09c3b2986472130f30aa0bfaf7f3980637","required":false,"strategy":"string"},{"pattern":"TERM=xterm","required":false,"strategy":"string"},{"pattern":"((?i)FABRIC)_.+=.+","required":false,"strategy":"re2"},{"pattern":"HOSTNAME=.+","required":false,"strategy":"re2"},{"pattern":"T(E)?MP=.+","required":false,"strategy":"re2"},{"pattern":"FabricPackageFileName=.+","required":false,"strategy":"re2"},{"pattern":"HostedServiceName=.+","required":false,"strategy":"re2"},{"pattern":"IDENTITY_API_VERSION=.+","required":false,"strategy":"re2"},{"pattern":"IDENTITY_HEADER=.+","required":false,"strategy":"re2"},{"pattern":"IDENTITY_SERVER_THUMBPRINT=.+","required":false,"strategy":"re2"},{"pattern":"azurecontainerinstance_restarted_by=.+","required":false,"strategy":"re2"}],"exec_processes":[],"id":"caciexamples.azurecr.io/simple_server:latest","layers":["0f19124c0d8829b46174ad389daa9c83c1b35eac1f90c0e62a6c258a7f407098","20263bc88a55a6ebdf6b166df02f84c3c0bc06524c290697363837b0c5aa760f","80cfbf245f5bb30d902d412446f56786f60e939ce5c234c757ba33709ceaf997","029bfe57ee984a7d7a6d9eda05cd5dc1da0dc58cb0f39cd5894232a50efe31fd","079813b3da38f0b1853a49854c3cb4471a5612a915bb08b4ca8cf3c92060cbc5","d4da12f342c6bd854d5be5fe55b667e45f0f391e0bcdbb3dc741a3282f9e7c8d","1d3c13611dcd178189ec7bc39656684b6ddb0be570481828c4074af5d2ce88fd","4d7ea0af95b11bec6847553dabf314117537b7aeb8b9ea0c340bbad840e1978b","54e8f5317ac5cbf8ab0c3381dd7fe04032d28167ba3b443d85f277fe80f177ef","8c0a8e37ef67262a36cdb43a8fc02227718b2e77d96b888d63f0b9563f3b59f3","5cccc93a444912889a278cdb04b88cefe408bca93e43e0d05c2e35369257d2cd"],"mounts":[{"destination":"/etc/resolv.conf","options":["rbind","rshared","rw"],"source":"sandbox:///tmp/atlas/resolvconf/.+","type":"bind"}],"signals":[],"working_dir":"/app"},{"allow_elevated":false,"allow_stdio_access":true,"command":["/pause"],"env_rules":[{"pattern":"PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin","required":true,"strategy":"string"},{"pattern":"TERM=xterm","required":false,"strategy":"string"}],"exec_processes":[],"layers":["16b514057a06ad665f92c02863aca074fd5976c755d26bff16365299169e8415"],"mounts":[],"signals":[],"working_dir":"/"}]

allow_properties_access := false
allow_dump_stacks := false
allow_runtime_logging := false
allow_environment_variable_dropping := true
allow_unencrypted_scratch := false



mount_device := data.framework.mount_device
unmount_device := data.framework.unmount_device
mount_overlay := data.framework.mount_overlay
unmount_overlay := data.framework.unmount_overlay
create_container := data.framework.create_container
exec_in_container := data.framework.exec_in_container
exec_external := data.framework.exec_external
shutdown_container := data.framework.shutdown_container
signal_container_process := data.framework.signal_container_process
plan9_mount := data.framework.plan9_mount
plan9_unmount := data.framework.plan9_unmount
get_properties := data.framework.get_properties
dump_stacks := data.framework.dump_stacks
runtime_logging := data.framework.runtime_logging
load_fragment := data.framework.load_fragment
scratch_mount := data.framework.scratch_mount
scratch_unmount := data.framework.scratch_unmount

reason := {"errors": data.framework.errors}