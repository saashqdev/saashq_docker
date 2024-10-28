import os
import re


def get_versions():
    saashq_version = os.getenv("SAASHQ_VERSION")
    erpnexus_version = os.getenv("ERPNEXUS_VERSION")
    assert saashq_version, "No Saashq version set"
    assert erpnexus_version, "No ERPNexus version set"
    return saashq_version, erpnexus_version


def update_pwd(saashq_version: str, erpnexus_version: str):
    with open("pwd.yml", "r+") as f:
        content = f.read()
        content = re.sub(
            rf"saashq/erpnexus:.*", f"saashq/erpnexus:{erpnexus_version}", content
        )
        f.seek(0)
        f.truncate()
        f.write(content)


def main() -> int:
    update_pwd(*get_versions())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
