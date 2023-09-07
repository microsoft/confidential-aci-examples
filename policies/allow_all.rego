package policy

import future.keywords.every
import future.keywords.in

api_svn := "0.10.0"
framework_svn := "0.1.0"

allow_properties_access := true
allow_dump_stacks := true
allow_runtime_logging := true
allow_environment_variable_dropping := true
allow_unencrypted_scratch := true

mount_device := {"allowed": true}
unmount_device := {"allowed": true}
mount_overlay := {"allowed": true}
unmount_overlay := {"allowed": true}
create_container := {"allowed": true, "env_list": null, "allow_stdio_access": true}
exec_in_container := {"allowed": true}
exec_external := {"allowed": true, "env_list": null, "allow_stdio_access": true}
shutdown_container := {"allowed": true}
signal_container_process := {"allowed": true}
plan9_mount := {"allowed": true}
plan9_unmount := {"allowed": true}
get_properties := {"allowed": true}
dump_stacks := {"allowed": true}
runtime_logging := {"allowed": true}
load_fragment := {"allowed": true}
scratch_mount := {"allowed": true}
scratch_unmount := {"allowed": true}

reason := {"errors": {"allowed": true}}
