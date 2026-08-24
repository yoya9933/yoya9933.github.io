from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"


def main() -> int:
    errors: list[str] = []
    required_files = [
        SITE / "assets/avatar-fallback.svg",
        SITE / "assets/main.js",
    ]
    for path in required_files:
        if not path.exists():
            errors.append(f"missing P3 asset: {path.relative_to(SITE)}")

    html_files = sorted(SITE.rglob("*.html"))
    for path in html_files:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(SITE)
        if "data-theme-bootstrap" not in text:
            errors.append(f"missing early theme bootstrap: {rel}")
        if 'name="theme-color"' not in text:
            errors.append(f"missing theme-color meta: {rel}")
        if "menu-toggle" in text and "aria-label=" not in text:
            errors.append(f"menu toggle lacks initial accessible label: {rel}")
        if "data-theme-toggle" in text and "aria-pressed=" not in text:
            errors.append(f"theme toggle lacks initial pressed state: {rel}")

    home = (SITE / "index.html").read_text(encoding="utf-8")
    if 'data-avatar-fallback="/assets/avatar-fallback.svg"' not in home:
        errors.append("home profile avatar lacks local fallback wiring")

    js = (SITE / "assets/main.js").read_text(encoding="utf-8") if (SITE / "assets/main.js").exists() else ""
    for token in ("themeMeta", "aria-pressed", "data-avatar-fallback"):
        if token not in js:
            errors.append(f"runtime missing P3 behavior token: {token}")

    if errors:
        print("P3 checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"P3 checks passed for {len(html_files)} HTML files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
