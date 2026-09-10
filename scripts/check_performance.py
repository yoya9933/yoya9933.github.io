from __future__ import annotations

from pathlib import Path
import json
import re
import struct

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
DATA = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
PROJECTS = DATA["projects"]
PROFILE_IMAGE = "assets/profile.jpg"


def png_dimensions(path: Path) -> tuple[int, int] | None:
    try:
        header = path.read_bytes()[:24]
    except OSError:
        return None
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", header[16:24])


def jpeg_dimensions(path: Path) -> tuple[int, int] | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if len(data) < 4 or not data.startswith(b"\xff\xd8") or not data.endswith(b"\xff\xd9"):
        return None

    sof_markers = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    offset = 2
    while offset < len(data):
        if data[offset] != 0xFF:
            return None
        while offset < len(data) and data[offset] == 0xFF:
            offset += 1
        if offset >= len(data):
            return None

        marker = data[offset]
        offset += 1
        if marker == 0xDA:
            break
        if marker in {0x01, 0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
            continue
        if offset + 2 > len(data):
            return None

        segment_length = struct.unpack(">H", data[offset:offset + 2])[0]
        if segment_length < 2 or offset + segment_length > len(data):
            return None
        if marker in sof_markers:
            if segment_length < 7:
                return None
            height, width = struct.unpack(">HH", data[offset + 3:offset + 7])
            return (width, height) if width > 0 and height > 0 else None
        offset += segment_length
    return None


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
        for match in re.finditer(r'<img\b[^>]*src="[^"]*assets/projects/([^/".]+)\.(?:webp|png|svg)"[^>]*>', text, re.I):
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

    profile_path = SITE / PROFILE_IMAGE
    profile_dimensions = jpeg_dimensions(profile_path)
    if not profile_dimensions:
        errors.append(f"local profile image is missing or invalid JPEG: {PROFILE_IMAGE}")
    elif min(profile_dimensions) < 156:
        errors.append(f"local profile image is too small: {profile_dimensions[0]}x{profile_dimensions[1]}")

    for rel, src in (("index.html", PROFILE_IMAGE), ("en/index.html", f"../{PROFILE_IMAGE}")):
        home = (SITE / rel).read_text(encoding="utf-8")
        match = re.search(rf'<img\b[^>]*src="{re.escape(src)}"[^>]*>', home, re.I)
        if not match:
            errors.append(f"local profile image missing from {rel}")
            continue
        tag = match.group(0)
        if 'width="156"' not in tag or 'height="156"' not in tag:
            errors.append(f"profile image intrinsic display dimensions missing from {rel}")
        if 'decoding="async"' not in tag:
            errors.append(f"profile image async decoding missing from {rel}")

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
    print(f"Performance & Quality checks passed for {len(PROJECTS)} projects with valid local profile photo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
