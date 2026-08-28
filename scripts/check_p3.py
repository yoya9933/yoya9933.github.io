from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
DATA = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
PROJECTS = DATA["projects"]
SELECTED = sorted((p for p in PROJECTS if p.get("section") == "selected"), key=lambda p: p["order"])


def main() -> int:
    errors: list[str] = []
    required_files = [
        SITE / "assets/avatar-fallback.svg",
        SITE / "assets/main.js",
        SITE / "assets/portfolio-extra.css",
    ]
    for project in PROJECTS:
        required_files.append(SITE / "assets/projects" / project["image"])
        required_files.append(SITE / "assets/projects/snapshots" / project["image"])
    required_files.append(SITE / "assets/projects/shareholder-cms.png")

    for path in required_files:
        if not path.exists():
            errors.append(f"missing P3 asset: {path.relative_to(SITE)}")

    html_files = sorted(SITE.rglob("*.html"))
    for path in html_files:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(SITE)
        if 'data-theme="dark"' not in text:
            errors.append(f"published page is not fixed to dark theme: {rel}")
        if 'name="theme-color"' not in text or '#07111f' not in text:
            errors.append(f"missing dark theme-color meta: {rel}")
        if 'data-theme-toggle' in text:
            errors.append(f"legacy light-theme toggle leaked into published page: {rel}")
        if 'data-theme-bootstrap' in text:
            errors.append(f"legacy theme bootstrap leaked into published page: {rel}")
        if "menu-toggle" in text and "aria-label=" not in text:
            errors.append(f"menu toggle lacks initial accessible label: {rel}")

    home = (SITE / "index.html").read_text(encoding="utf-8")
    en_home = (SITE / "en/index.html").read_text(encoding="utf-8")
    for rel, text, locale in (("index.html", home, "zh"), ("en/index.html", en_home, "en")):
        for token in ("hero", "profile-card", "projects-grid", "project-card", "skill-groups", "timeline", "contact", "secondary-project"):
            if token not in text:
                errors.append(f"portfolio block {token!r} missing from {rel}")
        if "ncku-return-os" in text or "Credit Map" in text or "學分地圖" in text:
            errors.append(f"retired credit-map content remains in {rel}")
        for project in SELECTED:
            if f'data-project="{project["slug"]}"' not in text:
                errors.append(f"selected project {project['slug']!r} missing from {rel}")
            if project["title"][locale] not in text:
                errors.append(f"manifest title for {project['slug']!r} missing from {rel}")
        additional = [p for p in PROJECTS if p.get("section") == "additional"]
        for project in additional:
            if f'data-project="{project["slug"]}"' not in text:
                errors.append(f"additional project {project['slug']!r} missing from {rel}")
        if DATA["selected_heading"][locale] not in text:
            errors.append(f"manifest-selected heading copy missing from {rel}")
        if 'src="/assets/avatar-fallback.svg"' not in text:
            errors.append(f"local profile avatar missing from {rel}")
        if "https://github.com/yoya9933.png" in text:
            errors.append(f"third-party profile avatar leaked into {rel}")

    # Every case-study CTA must be rendered from the manifest.
    for project in PROJECTS:
        for locale in ("zh", "en"):
            case_path = SITE / project["case"][locale].lstrip("/") / "index.html"
            text = case_path.read_text(encoding="utf-8")
            if f'data-project-actions="{project["slug"]}"' not in text:
                errors.append(f"manifest-driven case actions missing: {case_path.relative_to(SITE)}")
            if project.get("live") and project["live"] not in text:
                errors.append(f"live URL from manifest missing: {case_path.relative_to(SITE)}")
            if project.get("repo") and project["repo"] not in text:
                errors.append(f"repo URL from manifest missing: {case_path.relative_to(SITE)}")

    demo = (SITE / "demos/event-checkin/index.html").read_text(encoding="utf-8")
    if "noindex,nofollow" not in demo or "SYNTHETIC DATA ONLY" not in demo:
        errors.append("event demo privacy labels are missing")

    js = (SITE / "assets/main.js").read_text(encoding="utf-8") if (SITE / "assets/main.js").exists() else ""
    if "portfolioTheme" in js or "prefers-color-scheme: light" in js or "data-theme-toggle" in js:
        errors.append("runtime still contains legacy light-theme behavior")
    if "projectsGrid" in js or "shareholder-cms" in js:
        errors.append("runtime project injection fallback still exists")
    if "data-avatar-fallback" in js:
        errors.append("obsolete avatar fallback runtime still exists")
    if "menu-toggle" not in js:
        errors.append("runtime missing menu-toggle behavior")

    sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    for project in PROJECTS:
        for locale in ("zh", "en"):
            url = DATA["site_url"].rstrip("/") + project["case"][locale]
            if url not in sitemap:
                errors.append(f"manifest case URL missing from sitemap: {url}")

    old_demo = "https://chuhe-xiangqi-online.bowersbayley13783.chatgpt.site"
    if old_demo in home or old_demo in en_home:
        errors.append("retired chess demo URL leaked into rendered homepage")

    if errors:
        print("P3 checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"P3 checks passed for {len(PROJECTS)} manifest projects across {len(html_files)} HTML files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
