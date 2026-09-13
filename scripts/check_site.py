from __future__ import annotations

from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import json
import os
import re
import sys

from common import ROOT, SITE, SEMVER_RE, case_output, case_url, env_int, expected_environment, load_projects, png_dimensions, project_image, selected_projects

DATA = load_projects()
PROJECTS = DATA["projects"]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
CHANGELOG_TEXT = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
RELEASE_VERSIONS = re.findall(r"^##\s+v(\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)\s+[—-]", CHANGELOG_TEXT, re.MULTILINE)

FORBIDDEN = (
    "your.name@example.com",
    "linkedin.com/in/your-id",
    "{{__TRUNK_ADDRESS__}}",
    "{{__TRUNK_WS_BASE__}}",
    "優選（冠軍）",
    "attendee-tokens.json",
    "attendees.generated.ts",
)

REQUIRED = [
    "index.html",
    "en/index.html",
    "contact/index.html",
    "en/contact/index.html",
    "changelog/index.html",
    "version.json",
    "robots.txt",
    "sitemap.xml",
    "demos/event-checkin/index.html",
    "demos/event-checkin/event-demo.css",
    "demos/event-checkin/event-demo.js",
    "assets/Yu_CV.pdf",
    "assets/styles.css",
    "assets/profile.jpg",
    "assets/projects/shareholder-cms.png",
    "assets/projects/shareholder-cms.svg",
    "assets/projects/event-checkin.png",
    "assets/projects/ai-media-pipeline.png",
]
for project in PROJECTS:
    REQUIRED.extend([
        f"projects/{project['slug']}/index.html",
        f"en/projects/{project['slug']}/index.html",
        f"assets/projects/{project_image(project)}",
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


def jpeg_dimensions(path: Path) -> tuple[int, int] | None:
    try:
        from PIL import Image
        with Image.open(path) as image:
            if image.format != "JPEG":
                return None
            return image.size
    except (OSError, ValueError):
        return None


def performance_errors() -> list[str]:
    errors: list[str] = []
    dimensions: dict[str, tuple[int, int]] = {}
    for project in PROJECTS:
        slug = project["slug"]
        size = png_dimensions(SITE / "assets" / "projects" / f"{slug}.png")
        if not size:
            errors.append(f"missing readable PNG dimensions for {slug}")
        else:
            dimensions[slug] = size

    for html in sorted(SITE.rglob("*.html")):
        text = html.read_text(encoding="utf-8")
        for match in re.finditer(r'<img\b[^>]*src="[^"]*assets/projects/([^/".]+)\.(?:webp|png|svg)"[^>]*>', text, re.I):
            slug, tag = match.group(1), match.group(0)
            size = dimensions.get(slug)
            if not size:
                continue
            width, height = size
            if f'width="{width}"' not in tag or f'height="{height}"' not in tag:
                errors.append(f"intrinsic dimensions mismatch for {slug} in {html.relative_to(SITE)}; expected {width}x{height}")
            if 'decoding="async"' not in tag:
                errors.append(f"async decoding missing for {slug} in {html.relative_to(SITE)}")

    profile_path = SITE / "assets" / "profile.jpg"
    size = jpeg_dimensions(profile_path)
    if not size:
        errors.append("local profile image is missing or invalid JPEG: assets/profile.jpg")
    elif min(size) < 156:
        errors.append(f"local profile image is too small: {size[0]}x{size[1]}")

    for rel, src in (("index.html", "assets/profile.jpg"), ("en/index.html", "../assets/profile.jpg")):
        path = SITE / rel
        if not path.is_file():
            continue
        match = re.search(rf'<img\b[^>]*src="{re.escape(src)}"[^>]*>', path.read_text(encoding="utf-8"), re.I)
        if not match:
            errors.append(f"local profile image missing from {rel}")
            continue
        tag = match.group(0)
        if 'width="156"' not in tag or 'height="156"' not in tag:
            errors.append(f"profile image intrinsic display dimensions missing from {rel}")
        if 'decoding="async"' not in tag:
            errors.append(f"profile image async decoding missing from {rel}")

    css = SITE / "assets" / "styles.css"
    if not css.is_file():
        errors.append("deployed styles.css missing")
    else:
        text = css.read_text(encoding="utf-8")
        if ":focus-visible" not in text:
            errors.append("global focus-visible styling missing from deployed CSS")
        if "prefers-reduced-motion: reduce" not in text:
            errors.append("reduced-motion rules missing from deployed CSS")
    return errors


def observability_errors() -> list[str]:
    errors: list[str] = []
    version_path, manifest_path = SITE / "version.json", SITE / "build-manifest.json"
    if not version_path.is_file():
        return ["version.json missing"]
    if not manifest_path.is_file():
        return ["build-manifest.json missing"]
    version = json.loads(version_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if version.get("version") != VERSION:
        errors.append("version.json version does not match VERSION")
    commit = version.get("commit")
    if commit != "local" and (not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit)):
        errors.append("version.json commit is not a full SHA or 'local'")
    if (manifest.get("version"), manifest.get("commit")) != (version.get("version"), version.get("commit")):
        errors.append("build manifest identity does not match version.json")
    if os.environ.get("GITHUB_ACTIONS") == "true":
        run_id, run_number = env_int("GITHUB_RUN_ID"), env_int("GITHUB_RUN_NUMBER")
        repository = os.environ.get("GITHUB_REPOSITORY", "")
        if version.get("run_id") != run_id:
            errors.append("version.json run_id does not match GitHub Actions")
        if version.get("run_number") != run_number:
            errors.append("version.json run_number does not match GitHub Actions")
        if version.get("ref") != os.environ.get("GITHUB_REF"):
            errors.append("version.json ref does not match GitHub Actions")
        if version.get("workflow_run") != f"https://github.com/{repository}/actions/runs/{run_id}":
            errors.append("version.json workflow_run URL is incorrect")
        if not version.get("workflow"):
            errors.append("version.json workflow name is missing in CI")
    else:
        for key in ("run_id", "run_number", "workflow_run"):
            if version.get(key) is not None:
                errors.append(f"local version.json unexpectedly contains {key}")
    return errors


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


def is_local_static_asset(value: str) -> bool:
    parsed = urlparse(value)
    if parsed.scheme or value.startswith("//"):
        return False
    return parsed.path.lower().endswith((".css", ".js"))


def main() -> int:
    errors: list[str] = []
    if not SITE.exists():
        print("_site does not exist; run scripts/build_site.sh first", file=sys.stderr)
        return 2

    if not SEMVER_RE.fullmatch(VERSION):
        errors.append(f"VERSION is not valid SemVer: {VERSION!r}")
    if not RELEASE_VERSIONS or RELEASE_VERSIONS[0] != VERSION:
        errors.append("CHANGELOG.md newest release does not match VERSION")

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
            build_time = published_version.get("build_time", "")
            try:
                parsed_build_time = datetime.fromisoformat(build_time)
            except (TypeError, ValueError):
                errors.append("version.json build_time is not valid ISO 8601")
            else:
                if parsed_build_time.tzinfo is None:
                    errors.append("version.json build_time is missing timezone information")
            if published_version.get("environment") != expected_environment():
                errors.append(
                    f"version.json environment is {published_version.get('environment')!r}; "
                    f"expected {expected_environment()!r}"
                )
            if published_version.get("changelog") != "https://yoya9933.page/changelog/":
                errors.append("version.json changelog does not point to the public changelog page")

    for retired in (SITE / "projects/ncku-return-os", SITE / "en/projects/ncku-return-os"):
        if retired.exists():
            errors.append(f"retired credit-map page leaked into deployment: {retired.relative_to(SITE)}")
    if (SITE / "dist").exists():
        errors.append("stale dist directory leaked into deployment artifact")
    if (SITE / "assets/Yu_CV_source.html").exists():
        errors.append("CV source HTML leaked into deployment artifact")

    html_files = sorted(SITE.rglob("*.html"))
    version_meta = f'name="application-version" content="{VERSION}"'
    seo_tokens = ('hreflang="x-default"', 'property="og:url"', 'property="og:locale"', 'name="twitter:title"', 'name="twitter:description"', 'name="twitter:image"')
    for html in html_files:
        text = html.read_text(encoding="utf-8")
        rel = html.relative_to(SITE)
        for token in FORBIDDEN:
            if token in text:
                errors.append(f"forbidden token {token!r} found in {rel}")
        if version_meta not in text:
            errors.append(f"website version metadata missing from {rel}")
        if 'rel="canonical"' in text:
            for token in seo_tokens:
                if token not in text:
                    errors.append(f"{rel}: missing {token}")
        if "<main" in text and ('class="skip-link"' not in text or not re.search(r'<main\b[^>]*id="main"', text, re.I)):
            errors.append(f"{rel}: missing skip-link/main target")
        if 'data-theme="dark"' not in text:
            errors.append(f"{rel}: published page is not fixed to dark theme")
        if 'name="theme-color"' not in text or '#07111f' not in text:
            errors.append(f"{rel}: missing dark theme-color meta")
        if "menu-toggle" in text and "aria-label=" not in text:
            errors.append(f"{rel}: menu toggle lacks initial accessible label")
        for tag in re.findall(r'<a\b[^>]*target="_blank"[^>]*>', text, re.I):
            if "noopener" not in tag or "noreferrer" not in tag:
                errors.append(f"{rel}: unsafe target=_blank link")
        parser = RefParser()
        parser.feed(text)
        for _, ref in parser.refs:
            if is_local_static_asset(ref):
                versions = parse_qs(urlparse(ref).query).get("v", [])
                if versions != [VERSION]:
                    errors.append(
                        f"local CSS/JS reference is not cache-busted with v={VERSION} "
                        f"in {rel}: {ref}"
                    )
            target = resolve_local(html, ref)
            if target is not None and not target.exists():
                errors.append(f"broken local reference in {rel}: {ref}")

    changelog_path = SITE / "changelog/index.html"
    if changelog_path.exists():
        changelog = changelog_path.read_text(encoding="utf-8")
        if f">v{VERSION}</h2>" not in changelog:
            errors.append("public changelog does not contain the current VERSION")
        if f"/releases/tag/v{VERSION}" not in changelog:
            errors.append("public changelog does not link the current GitHub Release")
        if len(RELEASE_VERSIONS) > 1:
            previous = RELEASE_VERSIONS[1]
            compare_path = f"/compare/v{previous}...v{VERSION}"
            if compare_path not in changelog:
                errors.append(f"public changelog does not compare v{previous} to v{VERSION}")

    selected = selected_projects(DATA)
    for rel, locale in (("index.html", "zh"), ("en/index.html", "en")):
        home_path = SITE / rel
        if not home_path.exists():
            continue
        home = home_path.read_text(encoding="utf-8")
        for token in ("hero", "profile-card", "projects-grid", "project-card", "skill-groups", "timeline", "contact"):
            if token not in home:
                errors.append(f"portfolio block {token!r} missing from {rel}")
        if "additional-work" in home or "secondary-project" in home:
            errors.append(f"retired standalone additional-work layout remains in {rel}")
        if "ncku-return-os" in home or "Credit Map" in home or "學分地圖" in home:
            errors.append(f"retired credit-map content remains in {rel}")
        profile_src = "../assets/profile.jpg" if locale == "en" else 'src="assets/profile.jpg"'
        if profile_src not in home:
            errors.append(f"local profile photo missing from {rel}")
        if 'class="site-version"' not in home or f">v{VERSION}</a>" not in home:
            errors.append(f"visible website version missing from footer in {rel}")
        if 'href="/changelog/"' not in home:
            errors.append(f"footer version does not link to /changelog/ in {rel}")
        for project in selected:
            if f'data-project="{project["slug"]}"' not in home:
                errors.append(f"manifest-selected project {project['slug']} missing from {rel}")
            if case_url(project, locale) not in home:
                errors.append(f"case-study link for {project['slug']} missing from {rel}")
            if project.get("live") and project["live"] not in home:
                errors.append(f"live link for {project['slug']} missing from {rel}")
            if project.get("repo") and project["repo"] not in home:
                errors.append(f"repo link for {project['slug']} missing from {rel}")
            if project["title"][locale] not in home:
                errors.append(f"manifest title for {project['slug']} missing from {rel}")
        if DATA["selected_heading"][locale] not in home:
            errors.append(f"manifest-selected heading copy missing from {rel}")

    for project in PROJECTS:
        for locale in ("zh", "en"):
            case_path = case_output(project, locale)
            if not case_path.exists():
                continue
            case = case_path.read_text(encoding="utf-8")
            if f'data-project-actions="{project["slug"]}"' not in case:
                errors.append(f"manifest-driven project actions missing from {case_path.relative_to(SITE)}")
            for required in (f'data-case-facts="{project["slug"]}"', f'data-case-framing="{project["slug"]}"', "00 / Project framing"):
                if required not in case:
                    errors.append(f"case study missing {required!r}: {case_path.relative_to(SITE)}")
            if project.get("case_facts") is None or project.get("case_frame") is None:
                errors.append(f"{project['slug']} missing case_facts or case_frame in data/projects.json")
            if project.get("live") and project["live"] not in case:
                errors.append(f"live URL from manifest missing: {case_path.relative_to(SITE)}")
            if project.get("repo") and project["repo"] not in case:
                errors.append(f"repo URL from manifest missing: {case_path.relative_to(SITE)}")
            if '"@type":"CreativeWork"' not in case or '"@type":"BreadcrumbList"' not in case:
                errors.append(f"project structured data missing from {case_path.relative_to(SITE)}")

    localized_pairs = [("index.html", "en/index.html", "/", "/en/") , ("contact/index.html", "en/contact/index.html", "/contact/", "/en/contact/")]
    for project in PROJECTS:
        localized_pairs.append((
            f"projects/{project['slug']}/index.html",
            f"en/projects/{project['slug']}/index.html",
            case_url(project, "zh"),
            case_url(project, "en"),
        ))
    for zh_rel, en_rel, zh_route, en_route in localized_pairs:
        zh_path, en_path = SITE / zh_rel, SITE / en_rel
        if not zh_path.is_file() or not en_path.is_file():
            continue
        zh_text = zh_path.read_text(encoding="utf-8")
        en_text = en_path.read_text(encoding="utf-8")
        zh_url, en_url = DATA["site_url"].rstrip("/") + zh_route, DATA["site_url"].rstrip("/") + en_route
        for locale, url, text, rel in (
            ("zh-Hant", zh_url, zh_text, zh_rel), ("en", en_url, zh_text, zh_rel),
            ("zh-Hant", zh_url, en_text, en_rel), ("en", en_url, en_text, en_rel),
        ):
            if f'hreflang="{locale}" href="{url}"' not in text:
                errors.append(f"{rel}: missing hreflang={locale} link to {url}")

    for rel in ("index.html", "en/index.html"):
        home = (SITE / rel).read_text(encoding="utf-8")
        for token in (
            'name="author" content="Yu"', 'name="robots" content="index,follow"',
            'property="og:image:type" content="image/png"', 'property="og:image:width" content="1200"',
            'property="og:image:height" content="630"', 'rel="apple-touch-icon"', 'rel="manifest"',
        ):
            if token not in home:
                errors.append(f"{rel}: missing shared homepage metadata {token!r}")

    for rel in ("projects/shareholder-cms/index.html", "en/projects/shareholder-cms/index.html"):
        case_path = SITE / rel
        if case_path.exists():
            case = case_path.read_text(encoding="utf-8")
            if "shareholder-cms.webp" not in case or "shareholder-cms.png" not in case:
                errors.append(f"shareholder CMS case study lacks screenshot/OG assets: {rel}")

    sitemap_path = SITE / "sitemap.xml"
    if sitemap_path.exists():
        sitemap = sitemap_path.read_text(encoding="utf-8")
        for url in (DATA["site_url"] + "/", DATA["site_url"] + "/en/", DATA["site_url"] + "/contact/", DATA["site_url"] + "/en/contact/"):
            if url not in sitemap:
                errors.append(f"sitemap missing {url}")
        if "ncku-return-os" in sitemap or "/demos/" in sitemap:
            errors.append("sitemap contains retired or noindex content")

    robots_path = SITE / "robots.txt"
    if robots_path.exists():
        robots = robots_path.read_text(encoding="utf-8")
        for token in ("User-agent: *", "Allow: /", f"Sitemap: {DATA['site_url']}/sitemap.xml"):
            if token not in robots:
                errors.append(f"robots.txt missing {token!r}")

    demo = (SITE / "demos/event-checkin/index.html").read_text(encoding="utf-8") if (SITE / "demos/event-checkin/index.html").exists() else ""
    demo_js = (SITE / "demos/event-checkin/event-demo.js").read_text(encoding="utf-8") if (SITE / "demos/event-checkin/event-demo.js").exists() else ""
    if "SYNTHETIC DATA ONLY" not in demo or "SYNTHETIC_DATA_ONLY" not in demo_js:
        errors.append("event demo lacks explicit synthetic-data safeguards")
    if "noindex,nofollow" not in demo:
        errors.append("event demo must remain excluded from indexing")
    if (SITE / "assets/main.js").exists():
        runtime_js = (SITE / "assets/main.js").read_text(encoding="utf-8")
        if "projectsGrid" in runtime_js or "shareholder-cms" in runtime_js:
            errors.append("runtime project injection fallback still exists")
        if "menu-toggle" not in runtime_js:
            errors.append("runtime missing menu-toggle behavior")
    if (SITE / "sitemap.xml").exists():
        sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
        for project in PROJECTS:
            for locale in ("zh", "en"):
                url = DATA["site_url"].rstrip("/") + case_url(project, locale)
                if url not in sitemap:
                    errors.append(f"manifest case URL missing from sitemap: {url}")
    old_demo = "https://chuhe-xiangqi-online.bowersbayley13783.chatgpt.site"
    for rel in ("index.html", "en/index.html"):
        home_path = SITE / rel
        if home_path.is_file() and old_demo in home_path.read_text(encoding="utf-8"):
            errors.append("retired chess demo URL leaked into rendered homepage")

    event_case = SITE / "projects/event-checkin/index.html"
    if event_case.is_file() and "24 筆虛構資料" not in event_case.read_text(encoding="utf-8"):
        errors.append("EventOps case framing must preserve the synthetic-data evidence boundary")
    ai_case = SITE / "projects/ai-media-pipeline/index.html"
    if ai_case.is_file() and "沒有把它強制成 publish blocker" not in ai_case.read_text(encoding="utf-8"):
        errors.append("AI pipeline case framing must preserve the unenforced quality-gate limitation")
    for token in ("臺灣綜合大學系統", "Taiwan Comprehensive University System"):
        if token in demo or token in demo_js:
            errors.append(f"event demo exposes production identity: {token!r}")

    errors.extend(performance_errors())
    errors.extend(observability_errors())

    if errors:
        print("Site checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Site checks passed for v{VERSION}, {len(PROJECTS)} manifest projects and {len(html_files)} HTML files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
