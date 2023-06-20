import pexpect


def copy_to_vm(
    ip_address: str,
    user_password: str,
    src_path: str,
    dest_path: str,
):
    process = pexpect.spawn(
        f"scp -o StrictHostKeyChecking=no -r {src_path} test-user@{ip_address}:{dest_path}"
    )
    process.expect(f"test-user@{ip_address}'s password: ")
    process.sendline(user_password)
    process.expect(pexpect.EOF)
    print(process.before.decode("utf-8"))


def run_on_vm(
    ip_address: str,
    user_password: str,
    command: str,
    timeout: int = 30,
):
    print(f"Running: {command}")
    process = pexpect.spawn(
        f"ssh -o StrictHostKeyChecking=no test-user@{ip_address} '{repr(command)}'"
    )
    process.expect(f"test-user@{ip_address}'s password: ")
    process.sendline(user_password)
    if timeout > 0:
        process.expect(pexpect.EOF, timeout=timeout)
    output = process.before.decode("utf-8")
    print(output)
    return output
