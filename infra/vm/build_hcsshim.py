import glob
import os
import shutil
import subprocess
import tempfile
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.vm.update_containerplat import update_package


def build_hcsshim(
    package_path: str,
    hcsshim_url: str,
):
    prev_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as hcsshim_dir:
        with update_package(package_path) as package_dir:
            os.chdir(hcsshim_dir)
            subprocess.check_output(
                f"git clone {hcsshim_url} github.com/Microsoft/hcsshim", shell=True
            )
            os.chdir("github.com/Microsoft/hcsshim")

            # Build Go targets
            os.environ["GOPATH"] = hcsshim_dir
            os.environ["GOOS"] = "windows"
            os.environ["GO_BUILD_FLAGS"] = "-tags=rego"
            for target in [
                "cmd/containerd-shim-runhcs-v1",
                "cmd/device-util",
                "cmd/jobobject-util",
                "cmd/ncproxy",
                "cmd/runhcs",
                "cmd/shimdiag",
                "internal/tools/grantvmgroupaccess",
                "internal/tools/zapdir",
            ]:
                subprocess.check_output(
                    f"go build github.com/Microsoft/hcsshim/{target}", shell=True
                )
            for file in glob.glob("*.exe"):
                shutil.copy(file, package_dir)

            # Build Userspace
            kernel_dir = "linux_kernel"
            os.mkdir(kernel_dir)
            subprocess.run(
                f'az artifacts universal download --organization "https://dev.azure.com/msazure/" --project "dcf1de98-e135-4121-8a6c-99b73705f581" --scope project --feed "ContainerPlat-Dev" --name "enlightened-linux" --version "0.1.5" --path {kernel_dir}',
                shell=True,
            )
            shutil.copy(
                f"{kernel_dir}/core-image-minimal-aci-rootfs.tar", "base.tar.gz"
            )
            subprocess.run("make all && make rootfs", shell=True)
            shutil.copy("out/initrd.img", f"{package_dir}/LinuxBootFiles/initrd.img")
            shutil.copy("out/rootfs.vhd", f"{package_dir}/LinuxBootFiles/rootfs.vhd")

    prev_dir = os.chdir(prev_dir)
