from __future__ import annotations

import re
import subprocess
import tomllib
from pathlib import Path



ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = ROOT / "pyproject.toml"
VERSION_RE = re.compile(r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?:-beta\.(?P<beta>\d+))?$")


def parse_version(version: str) -> tuple[int, int, int, int | None]:
    match = VERSION_RE.fullmatch(version)
    if not match:
        raise ValueError(f"Invalid version format: {version}")

    major = int(match.group("major"))
    minor = int(match.group("minor"))
    patch = int(match.group("patch"))
    beta = match.group("beta")
    return major, minor, patch, int(beta) if beta is not None else None


def compare_versions(new_version: str, current_version: str) -> int:
    """Compare two semantic versions with optional beta prerelease."""
    new_key = _version_key(new_version)
    current_key = _version_key(current_version)

    if new_key > current_key:
        return 1
    if new_key < current_key:
        return -1
    return 0


def _version_key(version: str) -> tuple[int, int, int, int, int]:
    major, minor, patch, beta = parse_version(version)
    is_stable = 1 if beta is None else 0
    beta_number = beta or 0
    return major, minor, patch, is_stable, beta_number


def main(argv: list[str] | None = None) -> int:
    _ = argv  # signature kept for parity with other scripts

    with PYPROJECT_PATH.open("rb") as file:
        pyproject = tomllib.load(file)
        pr_version = pyproject["project"]["version"]

    print(f"PR Version: {pr_version}")

    try:
        subprocess.run(
            ["git", "fetch", "origin", "main"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError:
        print("⚠️  Could not fetch origin/main. Skipping version comparison.")
        return 0

    try:
        git_show = subprocess.run(
            ["git", "show", "origin/main:pyproject.toml"],
            check=True,
            text=True,
            capture_output=True,
        )
        main_branch_pyproject = tomllib.loads(git_show.stdout)
        main_version = main_branch_pyproject["project"]["version"]
    except subprocess.CalledProcessError:
        print("⚠️  No pyproject.toml found on origin/main. Skipping version comparison.")
        return 0

    print(f"Main Branch Version: {main_version}")

    comparison_result = compare_versions(pr_version, main_version)
    if comparison_result <= 0:
        raise ValueError(
            f"PR version ({pr_version}) must be greater than the main branch version ({main_version})."
        )

    print(f"✅ PR version {pr_version} is greater than the main branch version {main_version}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
