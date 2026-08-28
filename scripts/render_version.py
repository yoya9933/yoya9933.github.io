from __future__ import annotations

from html import escape
from pathlib import Path
import json
import os
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
VERSION_FILE = ROOT / "VERSION"
REPOSITORY = "https://github.com/yoya9933/yoya9933.github.io"
SITE_URL = "https://yoya9933.page"


def read_version() -> str:
    version = VERSION_FILE.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", version):
        raise RuntimeError(f"VERSION is not valid SemVer: {version!r}")
    return version


def read_commit() -> str:
    candidate = os.environ.get("GITHUB_SHA", "").strip().lower()
    if re.fullmatch(r"[0-9a-f]{40}", candidate):
        return candidate
    try:
        candidate = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip().lower()
    except (OSError, subprocess.CalledProcessError):
        return "local"
    return candidate if re.fullmatch(r"[0-9a-f]{40}", candidate) else "local"


def ensure_version_meta(text: str, version: str) -> str:
    tag = f'<meta name="application-version" content="{escape(version, quote=True)}">'
    pattern = r'<meta\s+name="application-version"\s+content="[^"]*"[^>]*>'
    if re.search(pattern, text, flags=re.I):
        return re.sub(pattern, tag, text, count=1, flags=re.I)
    return text.replace("</head>", tag + "</head>", 1)


def footer_version(version: str, commit: str) -> str:
    changelog_url = "/changelog/"
    if commit == "local":
        commit_url = REPOSITORY
        commit_label = "local"
    else:
        commit_url = f"{REPOSITORY}/commit/{commit}"
        commit_label = commit[:7]
    return (
        '<span class="site-version" role="group" aria-label="Website version">'
        f'<a href="{changelog_url}">v{escape(version)}</a>'
        '<span aria-hidden="true">·</span>'
        f'<a href="{commit_url}" target="_blank" rel="noopener noreferrer">{escape(commit_label)}</a>'
        '</span>'
    )


def inject_footer(text: str, version: str, commit: str) -> str:
    text = re.sub(r'<span class="site-version"[^>]*>.*?</span>', '', text, flags=re.I | re.S)
    marker = "</div></footer>"
    if marker not in text:
        return text
    return text.replace(marker, footer_version(version, commit) + marker, 1)


def main() -> None:
    version = read_version()
    commit = read_commit()

    for path in sorted(SITE.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        text = ensure_version_meta(text, version)
        if path.relative_to(SITE).as_posix() in {"index.html", "en/index.html"}:
            text = inject_footer(text, version, commit)
        path.write_text(text, encoding="utf-8")

    payload = {
        "version": version,
        "commit": commit,
        "repository": REPOSITORY,
        "changelog": f"{SITE_URL}/changelog/",
        "source_changelog": f"{REPOSITORY}/blob/main/CHANGELOG.md",
        "release": f"{REPOSITORY}/releases/tag/v{version}",
        "commit_url": REPOSITORY if commit == "local" else f"{REPOSITORY}/commit/{commit}",
    }
    (SITE / "version.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Rendered website version v{version} ({commit[:7] if commit != 'local' else 'local'})")


if __name__ == "__main__":
    main()
