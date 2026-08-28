from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"


def main() -> int:
    errors: list[str] = []
    required_files = [
        SITE / "assets/avatar-fallback.svg",
        SITE / "assets/main.js",
        SITE / "assets/portfolio-extra.css",
        SITE / "assets/projects/buoy.webp",
        SITE / "assets/projects/chess.webp",
        SITE / "assets/projects/event-checkin.webp",
        SITE / "assets/projects/ai-media-pipeline.webp",
    ]
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
    for rel, text in (("index.html", home), ("en/index.html", en_home)):
        for token in ("hero", "profile-card", "projects-grid", "project-card", "skill-groups", "timeline", "contact", "secondary-project"):
            if token not in text:
                errors.append(f"portfolio block {token!r} missing from {rel}")
        if "ncku-return-os" in text or "Credit Map" in text or "學分地圖" in text:
            errors.append(f"retired credit-map content remains in {rel}")
        for token in ("event-checkin", "ai-media-pipeline"):
            if token not in text:
                errors.append(f"new project {token!r} missing from {rel}")
    if 'data-avatar-fallback="/assets/avatar-fallback.svg"' not in home:
        errors.append("home profile avatar lacks local fallback wiring")

    demo = (SITE / "demos/event-checkin/index.html").read_text(encoding="utf-8")
    if "noindex,nofollow" not in demo or "SYNTHETIC DATA ONLY" not in demo:
        errors.append("event demo privacy labels are missing")

    js = (SITE / "assets/main.js").read_text(encoding="utf-8") if (SITE / "assets/main.js").exists() else ""
    if "portfolioTheme" in js or "prefers-color-scheme: light" in js or "data-theme-toggle" in js:
        errors.append("runtime still contains legacy light-theme behavior")
    for token in ("data-avatar-fallback", "menu-toggle"):
        if token not in js:
            errors.append(f"runtime missing behavior token: {token}")

    if errors:
        print("P3 checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"P3 dark portfolio checks passed for {len(html_files)} HTML files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
