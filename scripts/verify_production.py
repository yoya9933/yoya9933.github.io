from __future__ import annotations

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json
import os
import sys
import time

BASE_URL = os.environ.get("PORTFOLIO_BASE_URL", "https://yoya9933.page").rstrip("/")
EXPECTED_VERSION = os.environ.get("EXPECTED_VERSION", "").strip()
EXPECTED_COMMIT = os.environ.get("EXPECTED_COMMIT", "").strip().lower()
ATTEMPTS = int(os.environ.get("SMOKE_ATTEMPTS", "12"))
DELAY = int(os.environ.get("SMOKE_DELAY_SECONDS", "5"))


def get(path: str, *, cache_key: str) -> tuple[int, bytes, str]:
    sep = "&" if "?" in path else "?"
    url = f"{BASE_URL}{path}{sep}smoke={cache_key}"
    request = Request(url, headers={"User-Agent": "Yoya-Portfolio-Deployment-Smoke/1.0", "Cache-Control": "no-cache"})
    with urlopen(request, timeout=15) as response:
        return response.status, response.read(), response.headers.get("Content-Type", "")


def main() -> int:
    if not EXPECTED_VERSION or not EXPECTED_COMMIT:
        print("EXPECTED_VERSION and EXPECTED_COMMIT are required", file=sys.stderr)
        return 2

    last_error = "production did not converge"
    for attempt in range(1, ATTEMPTS + 1):
        try:
            status, body, content_type = get("/version.json", cache_key=EXPECTED_COMMIT)
            if status != 200:
                raise RuntimeError(f"version.json HTTP {status}")
            if "json" not in content_type.lower():
                raise RuntimeError(f"version.json unexpected content type: {content_type}")
            version = json.loads(body.decode("utf-8"))
            if version.get("version") != EXPECTED_VERSION:
                raise RuntimeError(f"version mismatch: {version.get('version')!r}")
            if version.get("commit") != EXPECTED_COMMIT:
                raise RuntimeError(f"commit mismatch: {version.get('commit')!r}")
            if version.get("environment") != "production":
                raise RuntimeError(f"environment mismatch: {version.get('environment')!r}")

            status, manifest_body, manifest_type = get("/build-manifest.json", cache_key=EXPECTED_COMMIT)
            if status != 200 or "json" not in manifest_type.lower():
                raise RuntimeError("build-manifest.json is not available as JSON")
            manifest = json.loads(manifest_body.decode("utf-8"))
            if manifest.get("version") != EXPECTED_VERSION or manifest.get("commit") != EXPECTED_COMMIT:
                raise RuntimeError("build manifest identity does not match release")
            if not isinstance(manifest.get("file_count"), int) or manifest["file_count"] < 20:
                raise RuntimeError("build manifest file_count is unexpectedly small")

            for path in ("/", "/changelog/", "/projects/chess/"):
                page_status, page_body, _ = get(path, cache_key=EXPECTED_COMMIT)
                if page_status != 200 or len(page_body) < 500:
                    raise RuntimeError(f"smoke page failed: {path} HTTP {page_status} bytes={len(page_body)}")

            print(
                f"Production smoke passed for v{EXPECTED_VERSION} {EXPECTED_COMMIT[:7]} "
                f"with {manifest['file_count']} manifested files"
            )
            return 0
        except (HTTPError, URLError, TimeoutError, UnicodeDecodeError, json.JSONDecodeError, RuntimeError) as exc:
            last_error = str(exc)
            print(f"Smoke attempt {attempt}/{ATTEMPTS} not ready: {last_error}")
            if attempt < ATTEMPTS:
                time.sleep(DELAY)

    print(f"Production smoke failed: {last_error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
