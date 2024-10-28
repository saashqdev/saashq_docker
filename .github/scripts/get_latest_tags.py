from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from typing import Literal

Repo = Literal["saashq", "erpnexus"]
MajorVersion = Literal["12", "13", "14", "15", "develop"]


def get_latest_tag(repo: Repo, version: MajorVersion) -> str:
    if version == "develop":
        return "develop"
    regex = rf"v{version}.*"
    refs = subprocess.check_output(
        (
            "git",
            "-c",
            "versionsort.suffix=-",
            "ls-remote",
            "--refs",
            "--tags",
            "--sort=v:refname",
            f"https://github.com/saashqdev/{repo}",
            str(regex),
        ),
        encoding="UTF-8",
    ).split()[1::2]

    if not refs:
        raise RuntimeError(f'No tags found for version "{regex}"')
    ref = refs[-1]
    matches: list[str] = re.findall(regex, ref)
    if not matches:
        raise RuntimeError(f'Can\'t parse tag from ref "{ref}"')
    return matches[0]


def update_env(file_name: str, saashq_tag: str, erpnexus_tag: str | None = None):
    text = f"\nSAASHQ_VERSION={saashq_tag}"
    if erpnexus_tag:
        text += f"\nERPNEXUS_VERSION={erpnexus_tag}"

    with open(file_name, "a") as f:
        f.write(text)


def _print_resp(saashq_tag: str, erpnexus_tag: str | None = None):
    print(json.dumps({"saashq": saashq_tag, "erpnexus": erpnexus_tag}))


def main(_args: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", choices=["saashq", "erpnexus"], required=True)
    parser.add_argument(
        "--version", choices=["12", "13", "14", "15", "develop"], required=True
    )
    args = parser.parse_args(_args)

    saashq_tag = get_latest_tag("saashq", args.version)
    if args.repo == "erpnexus":
        erpnexus_tag = get_latest_tag("erpnexus", args.version)
    else:
        erpnexus_tag = None

    file_name = os.getenv("GITHUB_ENV")
    if file_name:
        update_env(file_name, saashq_tag, erpnexus_tag)
    _print_resp(saashq_tag, erpnexus_tag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
