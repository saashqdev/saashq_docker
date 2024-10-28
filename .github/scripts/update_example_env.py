import os
import re


def get_erpnexus_version():
    erpnexus_version = os.getenv("ERPNEXUS_VERSION")
    assert erpnexus_version, "No ERPNexus version set"
    return erpnexus_version


def update_env(erpnexus_version: str):
    with open("example.env", "r+") as f:
        content = f.read()
        content = re.sub(
            rf"ERPNEXUS_VERSION=.*", f"ERPNEXUS_VERSION={erpnexus_version}", content
        )
        f.seek(0)
        f.truncate()
        f.write(content)


def main() -> int:
    update_env(get_erpnexus_version())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
