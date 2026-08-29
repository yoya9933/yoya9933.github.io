from __future__ import annotations

from pathlib import Path
import json
import os
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def env_int(name: str) -> int | None:
    value = os.environ.get(name, "").strip()
    return int(value) if value.isdigit() else None


def main() -> int:
    errors: list[str] = []
    version_path = SITE / "version.json"
    manifest_path = SITE / "build-manifest.json"
    if not version_path.is_file():
        errors.append("version.json missing")
    if not manifest_path.is_file():
        errors.append("build-manifest.json missing")
    if errors:
        for error in errors:
            print(f"- {error}")
        return 1

    version = json.loads(version_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if version.get("version") != VERSION:
        errors.append("version.json version does not match VERSION")
    commit = version.get("commit")
    if commit != "local" and not isinstance(commit, str):
        errors.append("version.json commit is invalid")
    elif commit != "local" and not re.fullmatch(r"[0-9a-f]{40}", commit):
        errors.append("version.json commit is not a full SHA")

    if manifest.get("version") != version.get("version") or manifest.get("commit") != version.get("commit"):
        errors.append("build manifest identity does not match version.json")

    if os.environ.get("GITHUB_ACTIONS") == "true":
        expected_run_id = env_int("GITHUB_RUN_ID")
        expected_run_number = env_int("GITHUB_RUN_NUMBER")
        expected_ref = os.environ.get("GITHUB_REF")
        expected_repository = os.environ.get("GITHUB_REPOSITORY")
        if version.get("run_id") != expected_run_id:
            errors.append("version.json run_id does not match GitHub Actions")
        if version.get("run_number") != expected_run_number:
            errors.append("version.json run_number does not match GitHub Actions")
        if version.get("ref") != expected_ref:
            errors.append("version.json ref does not match GitHub Actions")
        expected_url = f"https://github.com/{expected_repository}/actions/runs/{expected_run_id}"
        if version.get("workflow_run") != expected_url:
            errors.append("version.json workflow_run URL is incorrect")
        if not version.get("workflow"):
            errors.append("version.json workflow name is missing in CI")
    else:
        for key in ("run_id", "run_number", "workflow_run"):
            if version.get(key) is not None:
                errors.append(f"local version.json unexpectedly contains {key}")

    if errors:
        print("Observability checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        f"Observability checks passed for v{VERSION} "
        f"({str(version.get('commit'))[:7]}) run={version.get('run_id') or 'local'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
