package policy

import future.keywords.every
import future.keywords.in

api_svn := "0.10.0"

framework_svn := "0.1.0"

fragments := [{
	"feed": "mcr.microsoft.com/aci/aci-cc-infra-fragment",
	"includes": ["containers"],
	"issuer": "did:x509:0:sha256:I__iuL25oXEVFdTP_aBLx_eT1RPHbCQ_ECBQfYZpt9s::eku:1.3.6.1.4.1.311.76.59.1.3",
	"minimum_svn": "1.0.0",
}]

containers := [
	{
		"allow_elevated": true,
		"allow_stdio_access": true,
		"command": [
			"python",
			"payload.py",
		],
		"env_rules": [
			{
				"pattern": "PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
				"required": false,
				"strategy": "string",
			},
			{
				"pattern": "LANG=C.UTF-8",
				"required": false,
				"strategy": "string",
			},
			{
				"pattern": "GPG_KEY=A035C8C19219BA821ECEA86B64E628F8D684696D",
				"required": false,
				"strategy": "string",
			},
			{
				"pattern": "PYTHON_VERSION=3.11.2",
				"required": false,
				"strategy": "string",
			},
			{
				"pattern": "PYTHON_PIP_VERSION=22.3.1",
				"required": false,
				"strategy": "string",
			},
			{
				"pattern": "PYTHON_SETUPTOOLS_VERSION=65.5.1",
				"required": false,
				"strategy": "string",
			},
			{
				"pattern": "PYTHON_GET_PIP_URL=https://github.com/pypa/get-pip/raw/d5cb0afaf23b8520f1bbcfed521017b4a95f5c01/public/get-pip.py",
				"required": false,
				"strategy": "string",
			},
			{
				"pattern": "PYTHON_GET_PIP_SHA256=394be00f13fa1b9aaa47e911bdb59a09c3b2986472130f30aa0bfaf7f3980637",
				"required": false,
				"strategy": "string",
			},
			{
				"pattern": "TERM=xterm",
				"required": false,
				"strategy": "string",
			},
			{
				"pattern": "((?i)FABRIC)_.+=.+",
				"required": false,
				"strategy": "re2",
			},
			{
				"pattern": "HOSTNAME=.+",
				"required": false,
				"strategy": "re2",
			},
			{
				"pattern": "T(E)?MP=.+",
				"required": false,
				"strategy": "re2",
			},
			{
				"pattern": "FabricPackageFileName=.+",
				"required": false,
				"strategy": "re2",
			},
			{
				"pattern": "HostedServiceName=.+",
				"required": false,
				"strategy": "re2",
			},
			{
				"pattern": "IDENTITY_API_VERSION=.+",
				"required": false,
				"strategy": "re2",
			},
			{
				"pattern": "IDENTITY_HEADER=.+",
				"required": false,
				"strategy": "re2",
			},
			{
				"pattern": "IDENTITY_SERVER_THUMBPRINT=.+",
				"required": false,
				"strategy": "re2",
			},
			{
				"pattern": "azurecontainerinstance_restarted_by=.+",
				"required": false,
				"strategy": "re2",
			},
		],
		"exec_processes": [],
		"id": "caciexamples.azurecr.io/simple_server:latest",
		"layers": [
			"43d7299217dea9db4a229f8a5af114bb409625cf625e0513bca84828a1c65aa0",
			"cef38c1cb733d6edfa851146908245748f0f69ebe457dc303e92b9dacab9e132",
			"608fc77bf5224533c63233da6e4ae918c177d35909580e3849104f1030b45c8c",
			"80e9e863d4f24777dba4f58fa482e259f29bb300060bcd2dee1c74837aab1899",
			"d9df6e7c1234ec684cfa57d5f7a414c4318c304389f1c7d4f3f16fa68f4820ff",
			"367bffed74be739a5171988d09fbed89be36d46d4666b3343c3e02dbe1fc5770",
			"e2406639910ea5e2ecb67a7bcf4e7ec208afe45ff39b9516a0c06948f3a99a3e",
			"39ddc95449c7f958977a146feb33223ad3d60527382583554280c8cde6d9adc0",
			"bb30233b466a0e70d56800e9a1121e38209d6c2e9fca5b00df5d8065097ae836",
			"721348080eb28dc4e33560ecc7f2b6a6a8280f3556a2f8fa498fc5fb17742bb0",
			"fc957566f15946bef5fb881d7ff344c7f935a240d4e2adcb27c404820995c082",
		],
		"mounts": [{
			"destination": "/etc/resolv.conf",
			"options": [
				"rbind",
				"rshared",
				"rw",
			],
			"source": "sandbox:///tmp/atlas/resolvconf/.+",
			"type": "bind",
		}],
		"signals": [],
		"working_dir": "/app",
	},
	{
		"allow_elevated": false,
		"allow_stdio_access": true,
		"command": ["/pause"],
		"env_rules": [
			{
				"pattern": "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
				"required": true,
				"strategy": "string",
			},
			{
				"pattern": "TERM=xterm",
				"required": false,
				"strategy": "string",
			},
		],
		"exec_processes": [],
		"layers": ["16b514057a06ad665f92c02863aca074fd5976c755d26bff16365299169e8415"],
		"mounts": [],
		"signals": [],
		"working_dir": "/",
	},
]

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
