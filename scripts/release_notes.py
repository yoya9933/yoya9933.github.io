from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
CHANGELOG = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", VERSION):
    raise SystemExit(f"Invalid SemVer in VERSION: {VERSION!r}")

pattern = re.compile(
    rf"^##\s+v{re.escape(VERSION)}\s+[—-]\s+.+?$\n(?P<body>.*?)(?=^##\s+v|\Z)",
    re.MULTILINE | re.DOTALL,
)
match = pattern.search(CHANGELOG)
if not match:
    raise SystemExit(f"CHANGELOG.md has no section for v{VERSION}")

body = match.group("body").strip()
if not body:
    raise SystemExit(f"CHANGELOG.md section for v{VERSION} is empty")

print(f"## Yoya Portfolio v{VERSION}\n")
print(body)
print(f"\nWebsite: https://yoya9933.page/\nChangelog: https://yoya9933.page/changelog/")
