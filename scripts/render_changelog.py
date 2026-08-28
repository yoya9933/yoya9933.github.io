from __future__ import annotations

from html import escape
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
CHANGELOG = ROOT / "CHANGELOG.md"
REPOSITORY = "https://github.com/yoya9933/yoya9933.github.io"

HEADER_RE = re.compile(r"^##\s+v(?P<version>\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)\s+[—-]\s+(?P<date>.+?)\s*$")


def inline(text: str) -> str:
    escaped = escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    return escaped


def parse_releases() -> list[dict[str, object]]:
    lines = CHANGELOG.read_text(encoding="utf-8").splitlines()
    releases: list[dict[str, object]] = []
    current: dict[str, object] | None = None

    for raw in lines:
        line = raw.strip()
        match = HEADER_RE.match(line)
        if match:
            current = {
                "version": match.group("version"),
                "date": match.group("date"),
                "paragraphs": [],
                "items": [],
            }
            releases.append(current)
            continue
        if current is None or not line:
            continue
        if line.startswith("- "):
            current["items"].append(line[2:])
        elif not line.startswith("#"):
            current["paragraphs"].append(line)

    if not releases:
        raise RuntimeError("CHANGELOG.md does not contain any release headings")
    return releases


def render_release(release: dict[str, object]) -> str:
    version = str(release["version"])
    date = str(release["date"])
    paragraphs = "".join(f"<p>{inline(str(text))}</p>" for text in release["paragraphs"])
    items = release["items"]
    bullet_html = ""
    if items:
        bullet_html = "<ul>" + "".join(f"<li>{inline(str(item))}</li>" for item in items) + "</ul>"
    release_url = f"{REPOSITORY}/releases/tag/v{version}"
    return (
        '<article class="case-card changelog-release">'
        f'<div class="changelog-release-head"><div><p class="eyebrow">RELEASE</p><h2>v{escape(version)}</h2></div>'
        f'<time datetime="{escape(date)}">{escape(date)}</time></div>'
        f"{paragraphs}{bullet_html}"
        f'<p><a href="{release_url}" target="_blank" rel="noopener noreferrer">GitHub Release ↗</a></p>'
        "</article>"
    )


def main() -> None:
    releases = parse_releases()
    cards = "".join(render_release(release) for release in releases)
    target = SITE / "changelog" / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)

    html = f'''<!DOCTYPE html><html lang="zh-Hant-TW"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>更新紀錄｜Yoya Portfolio</title><meta name="description" content="Yoya Portfolio 的正式網站版本、更新內容與 GitHub Release 紀錄。"><link rel="canonical" href="https://yoya9933.page/changelog/"><link rel="icon" href="../assets/favicon.svg"><meta property="og:type" content="website"><meta property="og:title" content="更新紀錄｜Yoya Portfolio"><meta property="og:description" content="網站版本、更新內容與 GitHub Release 紀錄。"><meta property="og:image" content="https://yoya9933.page/assets/og-image.png"><link rel="stylesheet" href="../assets/styles.css"><link rel="stylesheet" href="../assets/p1.css"><link rel="stylesheet" href="../assets/portfolio-extra.css"></head><body class="case-page"><nav class="case-nav shell"><a href="../">← 回首頁</a><span class="toolbar"><a href="{REPOSITORY}/blob/main/CHANGELOG.md" target="_blank" rel="noopener noreferrer">GitHub Changelog ↗</a></span></nav><header class="case-hero shell"><p class="eyebrow">CHANGELOG</p><h1>網站更新紀錄。</h1><p>每個正式版本都由 <code>VERSION</code>、<code>CHANGELOG.md</code>、Git tag 與 GitHub Release 對應，方便確認目前網站功能與版本來源。</p></header><main class="case-content shell"><section class="case-section"><div class="case-grid">{cards}</div></section></main><script src="../assets/main.js" defer></script></body></html>'''
    target.write_text(html, encoding="utf-8")
    print(f"Rendered {len(releases)} changelog release(s)")


if __name__ == "__main__":
    main()
