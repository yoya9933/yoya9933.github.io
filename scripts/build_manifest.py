from __future__ import annotations

from pathlib import Path
import json
import sys

from common import SITE, sha256

VERSION_PATH = SITE / "version.json"
MANIFEST_PATH = SITE / "build-manifest.json"


def build() -> None:
    if not VERSION_PATH.is_file():
        raise RuntimeError("version.json must exist before build-manifest.json is generated")
    version_info = json.loads(VERSION_PATH.read_text(encoding="utf-8"))

    files: list[dict[str, object]] = []
    total_bytes = 0
    for path in sorted(SITE.rglob("*")):
        if not path.is_file() or path == MANIFEST_PATH:
            continue
        rel = path.relative_to(SITE).as_posix()
        size = path.stat().st_size
        total_bytes += size
        files.append({"path": rel, "bytes": size, "sha256": sha256(path)})

    payload = {
        "version": version_info["version"],
        "commit": version_info["commit"],
        "build_time": version_info["build_time"],
        "environment": version_info["environment"],
        "file_count": len(files),
        "total_bytes": total_bytes,
        "files": files,
    }
    MANIFEST_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Built deployment manifest for {len(files)} files ({total_bytes} bytes)")


def check() -> int:
    errors: list[str] = []
    if not MANIFEST_PATH.is_file():
        print("build-manifest.json is missing", file=sys.stderr)
        return 2
    if not VERSION_PATH.is_file():
        print("version.json is missing", file=sys.stderr)
        return 2

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    version = json.loads(VERSION_PATH.read_text(encoding="utf-8"))
    for key in ("version", "commit", "build_time", "environment"):
        if manifest.get(key) != version.get(key):
            errors.append(f"manifest {key} does not match version.json")

    entries = manifest.get("files")
    if not isinstance(entries, list):
        errors.append("manifest files is not a list")
        entries = []

    paths: set[str] = set()
    total_bytes = 0
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("manifest contains a non-object file entry")
            continue
        rel = entry.get("path")
        if not isinstance(rel, str) or not rel or rel == "build-manifest.json" or rel in paths:
            errors.append(f"invalid/duplicate manifest path: {rel!r}")
            continue
        paths.add(rel)
        path = SITE / rel
        if not path.is_file():
            errors.append(f"manifest file is missing: {rel}")
            continue
        size = path.stat().st_size
        total_bytes += size
        if entry.get("bytes") != size:
            errors.append(f"size mismatch for {rel}")
        if entry.get("sha256") != sha256(path):
            errors.append(f"SHA-256 mismatch for {rel}")

    actual = {
        path.relative_to(SITE).as_posix()
        for path in SITE.rglob("*")
        if path.is_file() and path != MANIFEST_PATH
    }
    if paths != actual:
        errors.extend(f"file missing from manifest: {path}" for path in sorted(actual - paths))
        errors.extend(f"manifest references unexpected file: {path}" for path in sorted(paths - actual))
    if manifest.get("file_count") != len(actual):
        errors.append("manifest file_count is incorrect")
    if manifest.get("total_bytes") != total_bytes:
        errors.append("manifest total_bytes is incorrect")

    if errors:
        print("Build manifest checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Build manifest checks passed for {len(actual)} files")
    return 0


def main() -> None:
    if "--check" in sys.argv[1:]:
        raise SystemExit(check())
    build()


if __name__ == "__main__":
    main()
