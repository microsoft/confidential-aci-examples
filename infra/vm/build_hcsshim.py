import glob
import os
import shutil
import subprocess
import tempfile
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.vm.get_containerplat import update_package


def build_hcsshim(
    package_path: str,
    hcsshim_url: str,
):
    with tempfile.TemporaryDirectory() as hcsshim_dir:
        with update_package(package_path) as package_dir:
            os.chdir(hcsshim_dir)
            subprocess.check_output(
                f"git clone {hcsshim_url} github.com/Microsoft/hcsshim", shell=True
            )
            os.chdir("github.com/Microsoft/hcsshim")
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
