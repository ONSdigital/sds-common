from __future__ import annotations

import re
import sys
from pathlib import Path

import tomllib


ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = ROOT / "pyproject.toml"
VERSION_RE = re.compile(r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?:-beta\.(?P<beta>\d+))?$")


def parse_version(version: str) -> tuple[int, int, int, int | None]:
    match = VERSION_RE.fullmatch(version)
    if not match:
        raise ValueError(f"Unsupported version format: {version}")

    major = int(match.group("major"))
    minor = int(match.group("minor"))
    patch = int(match.group("patch"))
    beta = match.group("beta")
    return major, minor, patch, int(beta) if beta is not None else None


def format_version(major: int, minor: int, patch: int, beta: int | None = None) -> str:
    version = f"{major}.{minor}.{patch}"
    return f"{version}-beta.{beta}" if beta is not None else version


def bump_stable(version: str, part: str = "patch") -> str:
    major, minor, patch, _beta = parse_version(version)

    if part == "major":
        return format_version(major + 1, 0, 0)
    if part == "minor":
        return format_version(major, minor + 1, 0)
    if part == "patch":
        return format_version(major, minor, patch + 1)

    raise ValueError(f"Unsupported bump part: {part}")


def bump_beta(version: str, part: str = "patch") -> str:
    major, minor, patch, beta = parse_version(version)

    if beta is not None:
        return format_version(major, minor, patch, beta + 1)

    stable_version = bump_stable(version, part=part)
    return f"{stable_version}-beta.1"


def remove_beta(version: str) -> str:
    major, minor, patch, _beta = parse_version(version)
    return format_version(major, minor, patch)


def update_pyproject_version(new_version: str, path: Path = PYPROJECT_PATH) -> str:
    current_version = read_project_version(path)
    updated = re.sub(
        r'(?m)^(version\s*=\s*")[^"]*(")$',
        rf'\g<1>{new_version}\g<2>',
        path.read_text(),
        count=1,
    )

    if updated == path.read_text():
        raise ValueError("Could not update pyproject.toml version line.")

    path.write_text(updated)
    return current_version


def read_project_version(path: Path = PYPROJECT_PATH) -> str:
    with path.open("rb") as f:
        pyproject = tomllib.load(f)

    return pyproject["project"]["version"]


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    mode = args[0] if args else "patch"
    part = args[1] if len(args) > 1 else "patch"

    current_version = read_project_version(PYPROJECT_PATH)

    if mode in {"major", "minor", "patch"}:
        new_version = bump_stable(current_version, part=mode)
    elif mode == "beta":
        new_version = bump_beta(current_version, part=part)
    elif mode == "remove-beta":
        new_version = remove_beta(current_version)
    else:
        raise SystemExit(
            "Usage: python bump_version.py [major|minor|patch|beta [major|minor|patch]|remove-beta]"
        )

    update_pyproject_version(new_version, PYPROJECT_PATH)

    print(f"Version bumped: {current_version} → {new_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
