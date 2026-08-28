from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
DATA = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
PROJECTS = DATA["projects"]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()

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
    "changelog/index.html",
    "version.json",
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

    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", VERSION):
        errors.append(f"VERSION is not valid SemVer: {VERSION!r}")

    for rel in REQUIRED:
        if not (SITE / rel).exists():
            errors.append(f"missing required output: {rel}")

    version_path = SITE / "version.json"
    if version_path.exists():
        try:
            published_version = json.loads(version_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"version.json is invalid JSON: {exc}")
        else:
            if published_version.get("version") != VERSION:
                errors.append("version.json does not match VERSION")
            commit = published_version.get("commit", "")
            if commit != "local" and not re.fullmatch(r"[0-9a-f]{40}", commit):
                errors.append("version.json commit is neither a full Git SHA nor 'local'")
            if published_version.get("changelog") != "https://yoya9933.page/changelog/":
                errors.append("version.json changelog does not point to the public changelog page")

    for retired in (SITE / "projects/ncku-return-os", SITE / "en/projects/ncku-return-os"):
        if retired.exists():
            errors.append(f"retired credit-map page leaked into deployment: {retired.relative_to(SITE)}")
    if (SITE / "dist").exists():
        errors.append("stale dist directory leaked into deployment artifact")
    if (SITE / "assets/Yoya_CV_source.html").exists():
        errors.append("CV source HTML leaked into deployment artifact")

    html_files = sorted(SITE.rglob("*.html"))
    version_meta = f'name="application-version" content="{VERSION}"'
    for html in html_files:
        text = html.read_text(encoding="utf-8")
        for token in FORBIDDEN:
            if token in text:
                errors.append(f"forbidden token {token!r} found in {html.relative_to(SITE)}")
        if version_meta not in text:
            errors.append(f"website version metadata missing from {html.relative_to(SITE)}")
        parser = RefParser()
        parser.feed(text)
        for _, ref in parser.refs:
            target = resolve_local(html, ref)
            if target is not None and not target.exists():
                errors.append(f"broken local reference in {html.relative_to(SITE)}: {ref}")

    changelog_path = SITE / "changelog/index.html"
    if changelog_path.exists():
        changelog = changelog_path.read_text(encoding="utf-8")
        if f">v{VERSION}</h2>" not in changelog:
            errors.append("public changelog does not contain the current VERSION")
        if f"/releases/tag/v{VERSION}" not in changelog:
            errors.append("public changelog does not link the current GitHub Release")

    selected = sorted((p for p in PROJECTS if p.get("section") == "selected"), key=lambda p: p["order"])
    for rel, locale in (("index.html", "zh"), ("en/index.html", "en")):
        home_path = SITE / rel
        if not home_path.exists():
            continue
        home = home_path.read_text(encoding="utf-8")
        if 'class="site-version"' not in home or f">v{VERSION}</a>" not in home:
            errors.append(f"visible website version missing from footer in {rel}")
        if 'href="/changelog/"' not in home:
            errors.append(f"footer version does not link to /changelog/ in {rel}")
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

    print(f"Site checks passed for v{VERSION}, {len(PROJECTS)} manifest projects and {len(html_files)} HTML files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
