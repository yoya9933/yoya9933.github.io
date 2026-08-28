from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
DATA = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
PROJECTS = DATA["projects"]

FORBIDDEN = (
    "your.name@example.com",
    "linkedin.com/in/your-id",
    "{{__TRUNK_ADDRESS__}}",
    "{{__TRUNK_WS_BASE__}}",
    "優選（冠軍）",
    "attendee-tokens.json",
    "attendees.generated.ts",
    "臺灣綜合大學系統",
)

REQUIRED = [
    "index.html",
    "en/index.html",
    "contact/index.html",
    "en/contact/index.html",
    "demos/event-checkin/index.html",
    "demos/event-checkin/event-demo.css",
    "demos/event-checkin/event-demo.js",
    "assets/Yoya_CV.pdf",
    "assets/portfolio-extra.css",
    "assets/projects/shareholder-cms.png",
    "assets/projects/shareholder-cms.svg",
    "assets/projects/event-checkin.png",
    "assets/projects/ai-media-pipeline.png",
]
for project in PROJECTS:
    REQUIRED.extend([
        f"projects/{project['slug']}/index.html",
        f"en/projects/{project['slug']}/index.html",
        f"assets/projects/{project['image']}",
        f"assets/projects/snapshots/{project['image']}",
    ])


class RefParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        for attr in ("href", "src"):
            value = data.get(attr)
            if value:
                self.refs.append((attr, value))


def resolve_local(source: Path, value: str) -> Path | None:
    parsed = urlparse(value)
    if parsed.scheme in {"http", "https", "mailto", "tel", "data", "javascript"} or value.startswith("//"):
        return None
    path = parsed.path
    if not path or path.startswith("#"):
        return None
    if path.startswith("/"):
        candidate = SITE / path.lstrip("/")
    else:
        candidate = source.parent / path
    if path.endswith("/"):
        candidate = candidate / "index.html"
    elif candidate.is_dir():
        candidate = candidate / "index.html"
    return candidate.resolve()


def main() -> int:
    errors: list[str] = []
    if not SITE.exists():
        print("_site does not exist; run scripts/build_site.sh first", file=sys.stderr)
        return 2

    for rel in REQUIRED:
        if not (SITE / rel).exists():
            errors.append(f"missing required output: {rel}")

    for retired in (SITE / "projects/ncku-return-os", SITE / "en/projects/ncku-return-os"):
        if retired.exists():
            errors.append(f"retired credit-map page leaked into deployment: {retired.relative_to(SITE)}")
    if (SITE / "dist").exists():
        errors.append("stale dist directory leaked into deployment artifact")
    if (SITE / "assets/Yoya_CV_source.html").exists():
        errors.append("CV source HTML leaked into deployment artifact")

    html_files = sorted(SITE.rglob("*.html"))
    for html in html_files:
        text = html.read_text(encoding="utf-8")
        for token in FORBIDDEN:
            if token in text:
                errors.append(f"forbidden token {token!r} found in {html.relative_to(SITE)}")
        parser = RefParser()
        parser.feed(text)
        for _, ref in parser.refs:
            target = resolve_local(html, ref)
            if target is not None and not target.exists():
                errors.append(f"broken local reference in {html.relative_to(SITE)}: {ref}")

    selected = sorted((p for p in PROJECTS if p.get("section") == "selected"), key=lambda p: p["order"])
    for rel, locale in (("index.html", "zh"), ("en/index.html", "en")):
        home_path = SITE / rel
        if not home_path.exists():
            continue
        home = home_path.read_text(encoding="utf-8")
        for project in selected:
            if f'data-project="{project["slug"]}"' not in home:
                errors.append(f"manifest-selected project {project['slug']} missing from {rel}")
            if project["case"][locale] not in home:
                errors.append(f"case-study link for {project['slug']} missing from {rel}")
            if project.get("live") and project["live"] not in home:
                errors.append(f"live link for {project['slug']} missing from {rel}")
            if project.get("repo") and project["repo"] not in home:
                errors.append(f"repo link for {project['slug']} missing from {rel}")

    for project in PROJECTS:
        for locale in ("zh", "en"):
            case_path = SITE / project["case"][locale].lstrip("/") / "index.html"
            if not case_path.exists():
                continue
            case = case_path.read_text(encoding="utf-8")
            if f'data-project-actions="{project["slug"]}"' not in case:
                errors.append(f"manifest-driven project actions missing from {case_path.relative_to(SITE)}")

    for rel in ("projects/shareholder-cms/index.html", "en/projects/shareholder-cms/index.html"):
        case_path = SITE / rel
        if case_path.exists():
            case = case_path.read_text(encoding="utf-8")
            if "shareholder-cms.webp" not in case or "shareholder-cms.png" not in case:
                errors.append(f"shareholder CMS case study lacks screenshot/OG assets: {rel}")

    demo = (SITE / "demos/event-checkin/index.html").read_text(encoding="utf-8") if (SITE / "demos/event-checkin/index.html").exists() else ""
    demo_js = (SITE / "demos/event-checkin/event-demo.js").read_text(encoding="utf-8") if (SITE / "demos/event-checkin/event-demo.js").exists() else ""
    if "SYNTHETIC DATA ONLY" not in demo or "SYNTHETIC_DATA_ONLY" not in demo_js:
        errors.append("event demo lacks explicit synthetic-data safeguards")

    if errors:
        print("Site checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Site checks passed for {len(PROJECTS)} manifest projects and {len(html_files)} HTML files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
