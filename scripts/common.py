"""Shared paths and small parsing helpers for the portfolio build scripts."""
from __future__ import annotations

import hashlib
import json
import os
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
PROJECTS_PATH = ROOT / "data" / "projects.json"
SEMVER_RE = re.compile(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?")


def load_projects() -> dict:
    return json.loads(PROJECTS_PATH.read_text(encoding="utf-8"))


def case_output(project: dict, locale: str, site: Path = SITE) -> Path:
    prefix = "en/" if locale == "en" else ""
    return site / prefix / "projects" / project["slug"] / "index.html"


def case_url(project: dict, locale: str) -> str:
    prefix = "/en" if locale == "en" else ""
    return f"{prefix}/projects/{project['slug']}/"


def project_image(project: dict) -> str:
    return f"{project['slug']}.webp"


def selected_projects(data: dict) -> list[dict]:
    return sorted(data["projects"], key=lambda project: project["order"])


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def png_dimensions(path: Path) -> tuple[int, int] | None:
    try:
        header = path.read_bytes()[:24]
    except OSError:
        return None
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        return None
    width, height = struct.unpack(">II", header[16:24])
    return (width, height) if width > 0 and height > 0 else None


def env_int(name: str) -> int | None:
    value = os.environ.get(name, "").strip()
    return int(value) if value.isdigit() else None


def expected_environment() -> str:
    explicit = os.environ.get("PORTFOLIO_ENVIRONMENT", "").strip()
    if explicit:
        return explicit
    if os.environ.get("GITHUB_REF") == "refs/heads/main":
        return "production"
    if os.environ.get("GITHUB_ACTIONS") == "true":
        return "ci"
    return "local"


def insert_before_head_end(text: str, fragment: str) -> str:
    if "</head>" not in text.lower():
        raise RuntimeError("HTML document has no </head>")
    match = re.search(r"</head\s*>", text, flags=re.IGNORECASE)
    assert match is not None
    return text[:match.start()] + fragment + text[match.start():]
