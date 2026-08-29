from __future__ import annotations

from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
VERSION_PATH = SITE / "version.json"
MANIFEST_PATH = SITE / "build-manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
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


if __name__ == "__main__":
    main()
