from __future__ import annotations

from pathlib import Path
import json
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
DATA = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
PUBLIC = SITE / "assets" / "projects"
SNAPSHOTS = PUBLIC / "snapshots"


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True, stdout=subprocess.DEVNULL)


def publish_webp(project: dict, snapshot: Path) -> None:
    image = project["image"]
    if Path(image).suffix.lower() != ".webp":
        raise RuntimeError(f"project image must be WebP: {project['slug']} -> {image}")
    shutil.copy2(snapshot, PUBLIC / image)


def build_tracked(project: dict, media: dict) -> None:
    source = ROOT / media["source"]
    if not source.is_file():
        raise RuntimeError(f"tracked snapshot missing for {project['slug']}: {source}")
    snapshot = SNAPSHOTS / project["image"]
    shutil.copy2(source, snapshot)
    publish_webp(project, snapshot)
    png = PUBLIC / f"{project['slug']}.png"
    run("dwebp", str(snapshot), "-o", str(png))


def build_svg(project: dict, media: dict) -> None:
    source = ROOT / media["source"]
    if not source.is_file() or source.suffix.lower() != ".svg":
        raise RuntimeError(f"SVG source missing for {project['slug']}: {source}")
    width = int(media["width"])
    height = int(media["height"])
    quality = int(media.get("quality", 86))
    png = PUBLIC / f"{project['slug']}.png"
    snapshot = SNAPSHOTS / project["image"]
    run("rsvg-convert", "-w", str(width), "-h", str(height), str(source), "-o", str(png))
    run("cwebp", "-quiet", "-q", str(quality), str(png), "-o", str(snapshot))
    publish_webp(project, snapshot)
    shutil.copy2(source, PUBLIC / source.name)


def build_local_capture(project: dict, media: dict) -> None:
    source = SITE / media["source"]
    if not source.is_file():
        raise RuntimeError(f"local capture target missing for {project['slug']}: {source}")
    width = int(media["width"])
    height = int(media["height"])
    budget = int(media.get("virtual_time_budget", 3500))
    quality = int(media.get("quality", 84))
    snapshot = SNAPSHOTS / project["image"]
    png = PUBLIC / f"{project['slug']}.png"
    with tempfile.TemporaryDirectory(prefix="portfolio-media-") as tmp:
        capture = Path(tmp) / "capture.png"
        run(
            "google-chrome",
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            "--hide-scrollbars",
            "--run-all-compositor-stages-before-draw",
            f"--virtual-time-budget={budget}",
            f"--window-size={width},{height}",
            f"--screenshot={capture}",
            source.resolve().as_uri(),
        )
        if not capture.is_file() or capture.stat().st_size < 1024:
            raise RuntimeError(f"capture output is invalid for {project['slug']}")
        shutil.copy2(capture, png)
        run("cwebp", "-quiet", "-q", str(quality), str(capture), "-o", str(snapshot))
    publish_webp(project, snapshot)


def main() -> None:
    PUBLIC.mkdir(parents=True, exist_ok=True)
    SNAPSHOTS.mkdir(parents=True, exist_ok=True)
    builders = {
        "tracked_snapshot": build_tracked,
        "svg_render": build_svg,
        "local_capture": build_local_capture,
    }

    for project in DATA["projects"]:
        media = project.get("media")
        if not media:
            raise RuntimeError(f"project media plan missing: {project['slug']}")
        media_type = media.get("type")
        builder = builders.get(media_type)
        if builder is None:
            raise RuntimeError(f"unsupported media type for {project['slug']}: {media_type!r}")
        builder(project, media)
        webp = PUBLIC / project["image"]
        png = PUBLIC / f"{project['slug']}.png"
        if not webp.is_file() or webp.stat().st_size < 512:
            raise RuntimeError(f"published WebP invalid for {project['slug']}")
        if not png.is_file() or png.stat().st_size < 512:
            raise RuntimeError(f"published PNG invalid for {project['slug']}")

    print(f"Built media for {len(DATA['projects'])} manifest projects")


if __name__ == "__main__":
    main()
