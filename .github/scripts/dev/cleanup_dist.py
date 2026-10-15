from __future__ import annotations

from pathlib import Path
import shutil


def cleanup_dist(dist_name: str = "dist") -> None:
    dist_dir = Path(dist_name).resolve()
    cwd = Path.cwd().resolve()

    if dist_dir.parent != cwd or dist_dir.name != dist_name:
        raise SystemExit(f"Refusing to delete unexpected path: {dist_dir}")

    if not dist_dir.exists():
        return

    if not dist_dir.is_dir():
        raise SystemExit(f"Refusing to delete non-directory path: {dist_dir}")

    shutil.rmtree(dist_dir)


if __name__ == "__main__":
    cleanup_dist()

