from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
DATA = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
PUBLIC = SITE / "assets" / "projects"


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True, stdout=subprocess.DEVNULL)


def webp_path(project: dict) -> Path:
    image = project["image"]
    if Path(image).suffix.lower() != ".webp":
        raise RuntimeError(f"project image must be WebP: {project['slug']} -> {image}")
    return PUBLIC / image


def build_tracked(project: dict, media: dict) -> None:
    source = ROOT / media["source"]
    if not source.is_file():
        raise RuntimeError(f"tracked snapshot missing for {project['slug']}: {source}")
    webp = webp_path(project)
    shutil.copy2(source, webp)
    run("dwebp", str(webp), "-o", str(PUBLIC / f"{project['slug']}.png"))


def build_svg(project: dict, media: dict) -> None:
    source = ROOT / media["source"]
    if not source.is_file() or source.suffix.lower() != ".svg":
        raise RuntimeError(f"SVG source missing for {project['slug']}: {source}")
    png = PUBLIC / f"{project['slug']}.png"
    run("rsvg-convert", "-w", str(int(media["width"])), "-h", str(int(media["height"])), str(source), "-o", str(png))
    run("cwebp", "-quiet", "-q", str(int(media.get("quality", 86))), str(png), "-o", str(webp_path(project)))
    shutil.copy2(source, PUBLIC / source.name)


def build_local_capture(project: dict, media: dict) -> None:
    source = SITE / media["source"]
    if not source.is_file():
        raise RuntimeError(f"local capture target missing for {project['slug']}: {source}")
    png = PUBLIC / f"{project['slug']}.png"
    run(
        "google-chrome",
        "--headless=new",
        "--no-sandbox",
        "--disable-gpu",
        "--hide-scrollbars",
        "--run-all-compositor-stages-before-draw",
        f"--virtual-time-budget={int(media.get('virtual_time_budget', 3500))}",
        f"--window-size={int(media['width'])},{int(media['height'])}",
        f"--screenshot={png}",
        source.resolve().as_uri(),
    )
    if not png.is_file() or png.stat().st_size < 1024:
        raise RuntimeError(f"capture output is invalid for {project['slug']}")
    run("cwebp", "-quiet", "-q", str(int(media.get("quality", 84))), str(png), "-o", str(webp_path(project)))


def build_public_capture(project: dict, media: dict) -> None:
    url = media["url"]
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.path not in {"", "/"}:
        raise RuntimeError(f"public capture must target an HTTPS site root: {project['slug']} -> {url}")

    fallback_source = ROOT / media["fallback_source"]
    if not fallback_source.is_file() or fallback_source.suffix.lower() != ".svg":
        raise RuntimeError(f"public capture fallback missing for {project['slug']}: {fallback_source}")

    png = PUBLIC / f"{project['slug']}.png"
    try:
        subprocess.run(
            [
                "google-chrome",
                "--headless=new",
                "--no-sandbox",
                "--disable-gpu",
                "--hide-scrollbars",
                "--run-all-compositor-stages-before-draw",
                f"--virtual-time-budget={int(media.get('virtual_time_budget', 6000))}",
                f"--window-size={int(media['width'])},{int(media['height'])}",
                f"--screenshot={png}",
                url,
            ],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=int(media.get("timeout_seconds", 35)),
        )
        captured = png.is_file() and png.stat().st_size >= 1024
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        captured = False

    if not captured:
        print(f"{project['slug']} public capture unavailable; using reviewed SVG fallback")
        run(
            "rsvg-convert",
            "-w", str(int(media.get("fallback_width", media["width"]))),
            "-h", str(int(media.get("fallback_height", media["height"]))),
            str(fallback_source),
            "-o", str(png),
        )

    run("cwebp", "-quiet", "-q", str(int(media.get("quality", 84))), str(png), "-o", str(webp_path(project)))
    shutil.copy2(fallback_source, PUBLIC / fallback_source.name)


def main() -> None:
    PUBLIC.mkdir(parents=True, exist_ok=True)
    builders = {
        "tracked_snapshot": build_tracked,
        "svg_render": build_svg,
        "local_capture": build_local_capture,
        "public_site_capture": build_public_capture,
    }

    for project in DATA["projects"]:
        media = project.get("media")
        if not media:
            raise RuntimeError(f"project media plan missing: {project['slug']}")
        builder = builders.get(media.get("type"))
        if builder is None:
            raise RuntimeError(f"unsupported media type for {project['slug']}: {media.get('type')!r}")
        builder(project, media)
        webp = webp_path(project)
        png = PUBLIC / f"{project['slug']}.png"
        if not webp.is_file() or webp.stat().st_size < 512:
            raise RuntimeError(f"published WebP invalid for {project['slug']}")
        if not png.is_file() or png.stat().st_size < 512:
            raise RuntimeError(f"published PNG invalid for {project['slug']}")

    print(f"Built media for {len(DATA['projects'])} manifest projects")


if __name__ == "__main__":
    main()
