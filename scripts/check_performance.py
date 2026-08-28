from __future__ import annotations

from pathlib import Path
import json
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
DATA = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
PROJECTS = DATA["projects"]


def png_dimensions(path: Path) -> tuple[int, int] | None:
    try:
        header = path.read_bytes()[:24]
    except OSError:
        return None
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", header[16:24])


def main() -> int:
    errors: list[str] = []
    dimensions: dict[str, tuple[int, int]] = {}
    for project in PROJECTS:
        dim = png_dimensions(SITE / "assets" / "projects" / f"{project['slug']}.png")
        if not dim:
            errors.append(f"missing readable PNG dimensions for {project['slug']}")
        else:
            dimensions[project["slug"]] = dim

    for html in sorted(SITE.rglob("*.html")):
        text = html.read_text(encoding="utf-8")
        if "https://github.com/yoya9933.png" in text:
            errors.append(f"third-party GitHub avatar leaked into {html.relative_to(SITE)}")
        for match in re.finditer(r'<img\b[^>]*src="[^"]*assets/projects/(?:snapshots/)?([^/".]+)\.(?:webp|png)"[^>]*>', text, re.I):
            slug = match.group(1)
            tag = match.group(0)
            expected = dimensions.get(slug)
            if not expected:
                continue
            width, height = expected
            if f'width="{width}"' not in tag or f'height="{height}"' not in tag:
                errors.append(
                    f"intrinsic dimensions mismatch for {slug} in {html.relative_to(SITE)}; "
                    f"expected {width}x{height}"
                )
            if 'decoding="async"' not in tag:
                errors.append(f"async decoding missing for {slug} in {html.relative_to(SITE)}")

    for rel in ("index.html", "en/index.html"):
        home = (SITE / rel).read_text(encoding="utf-8")
        if 'src="/assets/avatar-fallback.svg"' not in home:
            errors.append(f"local Yoya avatar missing from {rel}")

    css_path = SITE / "assets" / "p1.css"
    if css_path.is_file():
        css = css_path.read_text(encoding="utf-8")
        if ":focus-visible" not in css:
            errors.append("global focus-visible styling missing from deployed CSS")
        if "prefers-reduced-motion: reduce" not in css:
            errors.append("reduced-motion rules missing from deployed CSS")
    else:
        errors.append("deployed p1.css missing")

    if errors:
        print("Performance & Quality checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Performance & Quality checks passed for {len(PROJECTS)} projects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
